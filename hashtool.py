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
        ret_val = subprocess.run(command, shell=True, capture_output=True, text=True)
        if verbose:
            print(ret_val.stdout[:-1])
        return ret_val.stdout[:-1]  # strip EOL

    def unique_hash(self, verbose=False):
        # git the shortest unique hash >= 8 bits
        command  = 'git rev-parse --short=2 HEAD'
        ret_val = subprocess.run(command, shell=True, capture_output=True, text=True)
        if verbose:
            print(ret_val.stdout[:-1])
        return ret_val.stdout[:-1]

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
    status = git_output.status()
    changes = git_output.are_changes()
    out_string = 'ffff'

    if changes:
        print('>>> WARNING: you have uncommited changes <<<')
        print('Using 0x'+out_string)

    if not changes:
        out_string = git_output.full_hash()
    # a text define
    full_hash_string = '#define GIT_FULL_HASH_STR "' + out_string + '"'
    # a numeric define
    full_hash_number = '#define GIT_FULL_HASH_NUM 0x' + out_string

    if not changes:
        out_string = git_output.unique_hash()
    # a text define
    short_hash_string = '#define GIT_UNIQUE_HASH_STR "' + out_string + '"'
    # a numeric define
    short_hash_number = '#define GIT_UNIQUE_HASH_NUM 0x' + out_string

    # truncate full result down to fixed lengths, overriding git
    # it's not guaranteed unique, but probably the most useful
    # 32-bit
    if not changes:
        out_string = git_output.double_hash()
    # a text define
    fixed_32_bit_hash_string = '#define GIT_HASH_32_BIT_STR "' + out_string + '"'
    # a numeric define
    fixed_32_bit_hash_number = '#define GIT_HASH_32_BIT_NUM 0x' + out_string

    # 16-bit
    if not changes:
        out_string = git_output.word_hash()
    # a text define
    fixed_16_bit_hash_string = '#define GIT_HASH_16_BIT_STR "' + out_string + '"'
    # a numeric define
    fixed_16_bit_hash_number = '#define GIT_HASH_16_BIT_NUM 0x' + out_string

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

# __main__ calls with the default arguments
if __name__ == "__main__":
    make_h()
