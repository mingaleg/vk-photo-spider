CLIENT_ID = '4435976'

OAUTH_LINK = "https://oauth.vk.com/authorize?\
client_id=%s&\
scope=friends,photos&\
redirect_uri=https://oauth.vk.com/blank.html&\
display=page&\
response_type=token" % CLIENT_ID

from os import path
from sys import argv
from os import system

TOKEN_PATH = path.join(path.dirname(argv[0]), '.vktoken')

if len(argv) > 1 and argv[1] == 'auth':
    print 'Enter token:'
    system('google-chrome-stable "%s"' % OAUTH_LINK)
    token = raw_input()
    open(TOKEN_PATH, 'w').write(token)

token = open(TOKEN_PATH).read().strip()

import vkontakte

vk = vkontakte.API(token=token)

def retry_exception(tries=3, IgnoreException=Exception, DefaultVal=[]):
    """ Decorator for ignoring exception from a function
    e.g.   @ignore_exception(DivideByZero)
    e.g.2. ignore_exception(DivideByZero)(Divide)(2/0)
    """
    def dec(function):
        def _dec(*args, **kwargs):
            ok = False
            t = tries
            while t and not ok:
                try:
                    return function(*args, **kwargs)
                    ok = True
                except IgnoreException:
                    ok = False
                t -= 1
            return DefaultVal
        return _dec
    return dec

re = retry_exception

def get_uid(user_id):
    return re()(vk.users.get)(user_ids=user_id)[0]['uid']

def proceed_album(owner_id, album_id, tagged=True):
    album = re()(vk.photos.get)(owner_id=owner_id, album_id=album_id, extended=1)
    if tagged:
        album = filter((lambda x: x['tags']['count']), album)
    for photo in album:
        yield photo

def proceed_friend(owner_id):
    albums = re()(vk.photos.getAlbums)(owner_id=owner_id)
    for album in albums:
        for photo in proceed_album(owner_id=owner_id, album_id=album['aid']):
            yield photo

def proceed_user(user_id):
    profile_id = get_uid(user_id)
    friends = re()(vk.friends.get)(user_id=profile_id)
    for friend in friends:
        for photo in proceed_friend(owner_id=friend):
            yield photo

def filter_tags(photos, user_id):
    user_id = get_uid(user_id)
    for photo in photos:
        tags = re()(vk.photos.getTags)(owner_id=photo['owner_id'], photo_id=photo['pid'])
        for tag in tags:
            if tag['uid'] == user_id:
                yield photo

def get_link(photo):
    return "http://vk.com/photo%s_%s" % (photo['owner_id'], photo['pid'])

id = argv[1]

for p in filter_tags(proceed_user(id), id):
    print get_link(p)
    fh = open('result', 'a')
    fh.write(get_link(p) + '\n')
    fh.close()
