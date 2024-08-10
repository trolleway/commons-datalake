
#from pywikibot.backports import Dict, List, Tuple

# The family of sites to be working on.
# Pywikibot will import families/xxx_family.py so if you want to change
# this variable, you have to ensure that such a file exists. You may use
# generate_family_file to create one.
family = 'commons'

# The site code (language) of the site to be working on.
mylang = 'commons'

# The dictionary usernames should contain a username for each site where you
# have a bot account. If you have a unique username for all sites of a
# family , you can use '*'
usernames['commons']['commons'] = 'Svetlov Artem'
usernames['wikidata']['wikidata'] = usernames['commons']['commons']

# The list of BotPasswords is saved in another file. Import it if needed.
# See https://www.mediawiki.org/wiki/Manual:Pywikibot/BotPasswords to know how
# use them.
password_file = None
