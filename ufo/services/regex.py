"""Regex module which provides regular expressions to validate client input."""

# Set jinja environment globals
EMAIL_VALIDATION_PATTERN = r'[^@]+@[^@]+.[^@]+'
# Key lookup for users and group allows email or unique id.
KEY_LOOKUP_PATTERN = r'([^@]+@[^@]+.[^@]+|[a-zA-Z0-9]+)'
PUBLIC_KEY_PATTERN = r'ssh-rsa AAAA[0-9A-Za-z+/]+[=]{0,3}'
PRIVATE_KEY_PATTERN = (r'-----BEGIN RSA PRIVATE KEY-----[0-9A-Za-z+\/=\r\n ]+'
                       r'-----END RSA PRIVATE KEY-----')
# For information on where this huge regex came from, see here:
# http://stackoverflow.com/a/17871737/2216222
IP_V6_REGEX = (r'(([0-9a-fA-F]{1,4}:){7,7}[0-9a-fA-F]{1,4}|'
               r'([0-9a-fA-F]{1,4}:){1,7}:|'
               r'([0-9a-fA-F]{1,4}:){1,6}:[0-9a-fA-F]{1,4}|'
               r'([0-9a-fA-F]{1,4}:){1,5}(:[0-9a-fA-F]{1,4}){1,2}|'
               r'([0-9a-fA-F]{1,4}:){1,4}(:[0-9a-fA-F]{1,4}){1,3}|'
               r'([0-9a-fA-F]{1,4}:){1,3}(:[0-9a-fA-F]{1,4}){1,4}|'
               r'([0-9a-fA-F]{1,4}:){1,2}(:[0-9a-fA-F]{1,4}){1,5}|'
               r'[0-9a-fA-F]{1,4}:((:[0-9a-fA-F]{1,4}){1,6})|'
               r':((:[0-9a-fA-F]{1,4}){1,7}|:)|'
               r'fe80:(:[0-9a-fA-F]{0,4}){0,4}%[0-9a-zA-Z]{1,}|'
               r'::(ffff(:0{1,4}){0,1}:){0,1}'
               r'((25[0-5]|(2[0-4]|1{0,1}[0-9]){0,1}[0-9])\.){3,3}'
               r'(25[0-5]|(2[0-4]|1{0,1}[0-9]){0,1}[0-9])|'
               r'([0-9a-fA-F]{1,4}:){1,4}:'
               r'((25[0-5]|(2[0-4]|1{0,1}[0-9]){0,1}[0-9])\.){3,3}'
               r'(25[0-5]|(2[0-4]|1{0,1}[0-9]){0,1}[0-9])'
               r')')
IP_V4_REGEX = (r'((25[0-5]|(2[0-4]|1{0,1}[0-9]){0,1}[0-9])\.){3,3}(25[0-5]|'
               r'(2[0-4]|1{0,1}[0-9]){0,1}[0-9])')
IP_ADDRESS_PATTERN = IP_V6_REGEX + r'|' + IP_V4_REGEX
REGEXES_AND_ERRORS_DICTIONARY =  {
    'emailValidationPattern': str(EMAIL_VALIDATION_PATTERN),
    'keyLookupPattern': str(KEY_LOOKUP_PATTERN),
    'publicKeyPattern': str(PUBLIC_KEY_PATTERN),
    'privateKeyPattern': str(PRIVATE_KEY_PATTERN),
    'ipAddressPattern': str(IP_ADDRESS_PATTERN),
}
