"""
Usage:
 * Go to following URL (replace Your_OpenID with your own OpenID) and log in:
   https://api.openmaru.com/delegate_key/springnote?app_id=71fcb7c8&openid=Your_OpenID
 * Copy your user key. (Don't give your key to anyone!)
 * Create Springnote object with your OpenID and key:
   sn = Springnote(Your_OpenID, Your_user_key)
 * Enjoy!

Alternative usage:
 * Get your own application key and user key from:
   http://api.openmaru.com/
"""
from .models import Springnote, SpringnoteException
