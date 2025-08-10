# hash.py
# This script collects the git hash number of the commit and optionally creates
# a *.h file using make_h() f for use by the firmware at compile time.
# It should be run before compiling the c code.
import subprocess

class git_commands():
    def __init__(self, word_size=16):
        # nybble conversion
        self.WORD = int(word_size / 4)
        self.DOUBLE = int(word_size / 2)
        # error trap with warning message on init
        self.status(False) # don't print if it passes

    def status(self, verbose=True):
        try:
            # does git work?
            command  = 'git status --porcelain -z'
            ret_val = subprocess.run(command, shell=True, capture_output=True, text=True)
            if verbose:
                print('git status')
                print(ret_val.stdout)
        except:
            # error message
            print('>>> WARNING: git status did not work. <<<')
        finally:
            return ret_val.stdout

    def are_changes(self,verbose=False):
        # null string only if clean status
        if self.status(verbose) == '':
            return False
        else:
            return True

    def full_hash(self, verbose=False):
        # git the full hash
        command  = 'git rev-parse HEAD'
        output = subprocess.run(command, shell=True, capture_output=True, text=True)
        ret_val = output.stdout[:-1]    # strip EOL
        if verbose:
            print(ret_val)
        return ret_val

    def unique_hash(self, verbose=False):
        # git the shortest unique hash >= 8 bits
        command  = 'git rev-parse --short=2 HEAD'
        output = subprocess.run(command, shell=True, capture_output=True, text=True)
        ret_val = output.stdout[:-1]    # strip EOL
        if verbose:
            print(ret_val)
        return ret_val

    def normal_hash(self, verbose=False):
        # git the full hash
        full = self.full_hash()
        return full[0:6]  # 24 bits = 6 nybbles

    def word_hash(self, verbose=False):
        # git the full hash
        full = self.full_hash()
        return full[0:self.WORD]

    def double_hash(self, verbose=False):
        # git the full hash
        full = self.full_hash()
        return full[0:self.DOUBLE]

def make_h(filename='git_hash.h'):
    git_output = git_commands(word_size=16)
    status = git_output.status(False)
    changes = git_output.are_changes()
    STALE_NUM = 'ffff'
    STALE_STR = 'stale-'

    if changes:
        print('>>> WARNING: you have uncommited changes <<<')
        print('Using 0x' + STALE_NUM + ' for numeric defines.')
        print('Prefixing string defines with \"' + STALE_STR + '\".')

    # formulate full hash #defines
    full_hash_string = '#define GIT_FULL_HASH_STR \"' 
    full_hash_number = '#define GIT_FULL_HASH_NUM 0x'
    if changes:
        full_hash_string += STALE_STR
        full_hash_number += STALE_NUM
    else:
        full_hash_number += git_output.full_hash()
    # finally         
    full_hash_string += git_output.full_hash() + '\"'
        
    # formulate unique hash #defines
    short_hash_string = '#define GIT_UNIQUE_HASH_STR \"'
    short_hash_number = '#define GIT_UNIQUE_HASH_NUM 0x'
    if changes:
        short_hash_string += STALE_STR
        short_hash_number += STALE_NUM
    else:
        short_hash_number += git_output.unique_hash()
    # finally         
    short_hash_string += git_output.unique_hash() + '\"'

    # formulate 32-bit hash #defines
    fixed_32_bit_hash_string = '#define GIT_HASH_32_BIT_STR \"'
    fixed_32_bit_hash_number = '#define GIT_HASH_32_BIT_NUM 0x'
    if changes:
        fixed_32_bit_hash_string += STALE_STR
        fixed_32_bit_hash_number += STALE_NUM
    else:
        fixed_32_bit_hash_number += git_output.double_hash()
    # finally         
    fixed_32_bit_hash_string += git_output.double_hash() + '\"'

    # formulate 16-bit hash #defines
    fixed_16_bit_hash_string = '#define GIT_HASH_16_BIT_STR \"'
    fixed_16_bit_hash_number = '#define GIT_HASH_16_BIT_NUM 0x'
    if changes:
        fixed_16_bit_hash_string += STALE_STR
        fixed_16_bit_hash_number += STALE_NUM
    else:
        fixed_16_bit_hash_number += git_output.word_hash()
    # finally         
    fixed_16_bit_hash_string += git_output.word_hash() + '\"'

    # formulate good-ol' 24-bit hash #defines
    fixed_24_bit_hash_string = '#define GIT_HASH_24_BIT_STR \"'
    fixed_24_bit_hash_number = '#define GIT_HASH_24_BIT_NUM 0x'
    if changes:
        fixed_24_bit_hash_string += STALE_STR
        fixed_24_bit_hash_number += STALE_NUM
    else:
        fixed_24_bit_hash_number += git_output.normal_hash()
    # finally         
    fixed_24_bit_hash_string += git_output.normal_hash() + '\"'

    # create hash.h file
    with open(filename, 'w') as h_file:
        h_file.write('/*\n')
        h_file.write(' *\n')
        h_file.write(' * This is a file which was auto-generated during build. DO NOT EDIT.\n')
        h_file.write(' * It contains a number which makes the compiled code traceable to a git commit.\n')
        h_file.write(' *\n')
        h_file.write(' */\n')
        if changes:
            h_file.write('#define GIT_CHANGES 1  /***** WARNING: you have uncommited changes *****/\n\n')
        h_file.write(full_hash_string+'\n')
        h_file.write(full_hash_number+'\n\n')
        h_file.write(short_hash_string+'\n')
        h_file.write(short_hash_number+'\n\n')
        h_file.write('/* These are to be used with fixed-sized variables. */\n')
        h_file.write('/* They may become non-unique in very large repositories, but who cares? */\n')
        h_file.write(fixed_32_bit_hash_string+'\n')
        h_file.write(fixed_32_bit_hash_number+'\n\n')
        h_file.write(fixed_16_bit_hash_string+'\n')
        h_file.write(fixed_16_bit_hash_number+'\n\n')
        h_file.write(fixed_24_bit_hash_string+'  // traditional style\n')
        h_file.write(fixed_24_bit_hash_number+'  //traditional style\n\n')

# __main__ calls with the default arguments
if __name__ == "__main__":
    make_h()
