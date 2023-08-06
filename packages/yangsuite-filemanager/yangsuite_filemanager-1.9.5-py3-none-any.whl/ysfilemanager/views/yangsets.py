import json
import warnings

from django.shortcuts import render
from django.http import JsonResponse, HttpResponse
from django.contrib.auth.decorators import login_required
from slugify import slugify

from ..filemanager import (
    YSYangSet, YSMutableYangSet, YSYangRepository,
    split_user_set,
    do_validation, validation_status,
)
from yangsuite import get_logger
from ysyangtree.ymodels import ALL_NODETYPES
try:
    from ysyangtree.yangsettree import (
        check_yangset_require_update, create_yangset_tree,
        delete_yangset_tree, get_yangset_tree
    )
except Exception:
    def check_yangset_require_update(*args):
        pass

    def create_yangset_tree(*args):
        pass

    def delete_yangset_tree(*args):
        pass

    def get_yangset_tree(*args):
        pass

log = get_logger(__name__)


@login_required
def manage_yangsets(request, yangset=None):
    """Manage yangsets."""
    return render(request, 'ysfilemanager/yangsets.html', {
        'yangset': yangset or '',
    })


@login_required
def get_yangsets(request):
    """Get the list of available yangsets.

    Superusers can modify all sets.
    Staff or active users can only modify their own sets.
    All users can read all sets.

    Args:
      request (django.http.HTTPRequest): HTTP GET request
    Returns:
      JsonResponse: with form::

           {'yangsets': {
            'user1': [
              {'name': "display name", 'slug': "user1+display-name"},
              {'name': "another name", 'slug': "user1+another-name"},
            ], 'user2': [...],}
    """
    readonly = request.GET.get('readonly')

    if request.user.is_superuser or readonly == 'true':
        return JsonResponse({'yangsets': YSYangSet.all_yangsets()})
    else:
        user = request.user.username
        return JsonResponse({
            'yangsets': {
                user: YSYangSet.user_yangsets(user)
            }})


def yangset_required(decoratee):
    """Decorator for views that expect a 'yangset' arg on the given request.

    If the yangset arg is provided and valid, it's split on ':' and passed
    into the decorated function as params 'owner' and 'setname'

    Returns:
      JsonResponse: if yangset parameter is missing or incorrect.
    """
    def decorated(request):
        if request.method == 'POST':
            yangset = request.POST.get('yangset')
        else:
            yangset = request.GET.get('yangset')

        if yangset in ['', None]:
            return JsonResponse({'reply': 'No yangset specified'}, status=400,
                                reason="No yangset specified")

        try:
            owner, setname = split_user_set(yangset)
        except ValueError:
            return JsonResponse({}, status=400,
                                reason="Invalid yangset string")

        return decoratee(request, owner, setname)
    return decorated


def check_data(data, expected):
    if not isinstance(data, expected):
        raise ValueError('Bad data type')


@login_required
@yangset_required
def get_yangset_contents(request, owner, setname):
    """Get the contents of a yangset.

    Superusers can get the listing for any set; regular users
    can only access their own sets. (TODO: not presently enforced)

    Args:
      request (django.http.HTTPRequest): HTTP GET request
    Returns:
      JsonResponse: {'modules': [{mod, rev}, {mod, rev}, ...],
                     'repository': owner+reponame}
    """
    try:
        ys = YSYangSet.load(owner, setname)
    except OSError:
        return JsonResponse({}, status=404, reason="No such yangset")
    return JsonResponse({
        'modules': [{"name": m[0], "revision": m[1]} for m in
                    ys.get_modules_and_revisions()],
        'repository': ys.repository.slug,
    })


@login_required
@yangset_required
def get_related_modules(request, owner, setname):
    """Get modules related to the members of the given YANG set.

    Args:
      request (django.http.HttpRequest): HTTP GET request,
        with param 'yangset' value 'owner:setname'

    Returns:
      JsonResponse: with keys ``augmenter_modules``,
      ``identity_deriving_modules``, ``upstream_modules``,
      and ``related_modules``, each storing a list of ``[name, revision]``.

      These lists are all non-intersecting sets of modules.
    """
    try:
        ys = YSMutableYangSet.load(owner, setname)
    except OSError:
        return JsonResponse({}, status=404, reason="No such yangset")

    # Discard file paths - just module + revision
    upstream_modules = [{'name': m[0], 'revision': m[1]}
                        for m in ys.upstream_modules()]
    augmenter_modules = [{'name': m[0], 'revision': m[1]}
                         for m in ys.augmenter_modules()]
    identity_deriving_modules = [{'name': m[0], 'revision': m[1]}
                                 for m in ys.identity_deriving_modules()]
    related_modules = [{'name': m[0], 'revision': m[1]}
                       for m in ys.related_modules()]
    # The upstream_modules, identity_deriving_modules, and augmenter_modules
    # may intersect, but we want these lists to be non-intersecting.
    # Let identities, then augmenters take precedence.
    upstream_modules = [entry for entry in upstream_modules
                        if entry not in augmenter_modules and
                        entry not in identity_deriving_modules]
    augmenter_modules = [entry for entry in augmenter_modules
                         if entry not in identity_deriving_modules]

    return JsonResponse({
        'identity_deriving_modules': identity_deriving_modules,
        'augmenter_modules': augmenter_modules,
        'upstream_modules': upstream_modules,
        'related_modules': related_modules,
    })


@login_required
def create_yangset(request):
    """Create a new YANG set.

    Args:
      request (django.http.HttpRequest): HTTP POST request,
        with params 'setname', 'repository', and 'source'

    Returns:
      JsonResponse: simple success/failure status
    """
    user = request.user.username
    setname = request.POST.get('setname')

    if not setname:
        return JsonResponse(
            {}, status=400, reason="YANG set name not specified")

    if slugify(setname) in [split_user_set(e['slug'])[1] for e
                            in YSYangSet.user_yangsets(user)]:
        return JsonResponse(
            {}, status=403,
            reason="User {0} already has a YANG set named '{1}'".format(
                user, setname))

    repository = request.POST.get('repository')
    if not repository:
        return JsonResponse({}, status=400, reason="No repository name given")

    # TODO: either permit cross-owner yangsets, or explicitly check user==user
    if repository not in [d['slug'] for d in
                          YSYangRepository.user_repos(user)]:
        return JsonResponse({}, status=404, reason="Repository not found")
    add_modules = {}
    modules = []
    source = request.POST.get('source')
    if source:
        try:
            src_ys = YSYangSet.load(*split_user_set(source))
        except (RuntimeError, ValueError):
            return JsonResponse({}, status=400,
                                reason="Invalid source yangset")
        except OSError:
            return JsonResponse({}, status=404,
                                reason="No such source yangset")
        # Use name/revision but not path in case source is a different repo
        modules = [m[:2] for m in src_ys.modules]
        add_modules = {"module": [module[0] for module in modules]}

    try:
        ys = YSMutableYangSet(user, setname, modules, repository=repository)
        ys.write()
    except Exception as exc:
        return JsonResponse({}, status=500, reason=str(exc))

    included_nodetypes = request.POST.getlist('included_nodetypes[]',
                                              ALL_NODETYPES)
    ref = request.GET.get('reference')
    if not ref:
        ref = request.user.username

    tree_status = check_yangset_require_update(user, setname, add_modules,
                                               ref)

    ysettree = None
    if tree_status is True:

        ysettree = create_yangset_tree(user, setname,
                                       add_modules, repository, ref,
                                       included_nodetypes)

        if ysettree:
            del ysettree

    return JsonResponse({
        'reply': 'YANG set "{0}:{1}" created successfully'.format(
            request.user.username, setname),
        'slug': ys.slug,
    })


@login_required
@yangset_required
def update_yangset(request, owner, setname):
    """Update the module set in the given YANG set.

    Args:
      request (django.http.HttpRequest): HTTP POST request
        with parameters 'yangset', 'modules', 'operation'.
    """
    try:
        ys = YSMutableYangSet.load(owner, setname)
    except OSError:
        return JsonResponse({}, status=404, reason="No such yangset")

    mods = request.POST.get('modules')
    raised_warnings = []
    if mods:
        try:
            mods = json.loads(mods)
        except ValueError:
            return JsonResponse(
                {}, status=400,
                reason="Invalid modules argument - must be a JSON list")

        operation = request.POST.get('operation', 'replace')

        try:
            with warnings.catch_warnings(record=True) as caught_warnings:
                if operation == 'replace':
                    ys.modules = mods
                elif operation == 'add':
                    ys.modules = ys.modules + mods
                else:
                    return JsonResponse({}, status=400,
                                        reason="Unknown/invalid operation")
                for warning in caught_warnings:
                    # Catch multiple revision warnings
                    details = warning.message.__str__().split('\n')
                    reason = details.pop(0)
                    raised_warnings.append({
                        'reason': reason,
                        'details': details,
                    })

        except ValueError as exc:
            # The 'reason' parameter ends at the first newline, so any other
            # content in the exception text is passed as data instead.
            details = str(exc).split('\n')
            reason = details.pop(0)
            return JsonResponse(
                {'details': details}, status=400, reason=reason)

    repository = request.POST.get('repository')
    if repository:
        try:
            ys.repository = repository
        except Exception as exc:
            return JsonResponse({'details': ''}, status=400, reason=str(exc))

    ys.write()

    add_modules = {
        "module": [ys.modules[x][0] for x in range(len(ys.modules))]}

    if request.method == 'POST':
        yangset = request.POST.get('yangset')
    else:
        yangset = request.GET.get('yangset')

    if yangset in ['', None]:
        return JsonResponse({'reply': 'No yangset specified'}, status=400,
                            reason="No yangset specified")

    included_nodetypes = request.POST.getlist('included_nodetypes[]',
                                              ALL_NODETYPES)

    ref = request.POST.get('reference')
    if not ref:
        if request.user.username != owner:
            ref = owner
        else:
            ref = request.user.username
    tree_status = check_yangset_require_update(owner, setname, ys.modules,
                                               ref)
    ysettree = None
    if tree_status is True:

        try:
            ysettree = create_yangset_tree(owner, setname,
                                           add_modules, repository, ref,
                                           included_nodetypes)
        except Exception as e:
            return JsonResponse({'errors': str(e)})

        if ysettree:
            del ysettree

    return JsonResponse({
        'warnings': raised_warnings,
    })


@login_required
@yangset_required
def delete_yangset(request, owner, setname):
    """Delete the given yang set

    Args:
        request (django.http.HTTPRequest): HTTP request
    """
    delete_yangset_tree(owner, setname)

    try:
        YSYangSet.delete(owner, setname)
        status = setname + ' deleted'
    except OSError:
        status = setname + ' not found'

    log.info('Result of deleting owner %s yangset %s: %s',
             owner, setname, status)

    return JsonResponse({'reply': status})


@login_required
def validate_yangset(request):
    """Validate the given YANG set."""
    if request.method == 'POST':
        return validate_yangset_post(request)
    else:
        return JsonResponse(validation_status(request.user.username))


@yangset_required
def validate_yangset_post(request, owner, setname):
    quick = request.POST.get('quick', 'false')
    try:
        ys = YSYangSet.load(owner, setname)
    except OSError:
        return JsonResponse({}, status=404, reason="No such yangset")
    return JsonResponse(do_validation(request.user.username, ys, quick))


@login_required
def show_yangset_module(request, yangset, module):
    """Render the contents of the requested YANG module in the given set."""
    try:
        ys = YSYangSet.load(*split_user_set(yangset))
    except OSError:
        return HttpResponse(status=404, reason="YANG set not found")
    except ValueError:
        return HttpResponse(status=400, reason="Invalid yangset parameter")
    module_path = ys.module_path(module)
    if not module_path:
        return HttpResponse(status=404, reason="Module not found")
    text = open(module_path).read()
    return render(request, 'ysfilemanager/module.html', {
        'yangset': yangset,
        'yangsetname': ys.setname,
        'module': module,
        'lines': text.split("\n"),
    })
