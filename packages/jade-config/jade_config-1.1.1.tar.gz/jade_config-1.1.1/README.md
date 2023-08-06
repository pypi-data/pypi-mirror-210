# Jade Config
A Python package to quickly and easily make configs, or other things that your program needs to remember.

We've all written data to a text file for later. Sometimes It's fine. Sometimes we read from each line trying to put more than one value in one file, then it gets confusing. This package is a quick and easy way to save data using the `shelve` module from the Python Standard Library.

This module uses no third-party libraries. It only uses the Standard Library so it downloads really quick.

On Windows, Jade Config, creates three files.
```
file.bak
file.dat
file.dir
```
On Mac, Jade Config creates only one.
```
file.db
```

## Usage
<hr>
Jade Config is very simple to use.

**Download it with:**
```
pip install jade-config
```

**Import it using:**
```
>>> from jade_config import config
```

**Create a file with:**
```
>>> file = config.Config("fileName", True)
```
Replace 'fileName' with the name of the file. You do not need to include any file extensions. The last parameter is an optional logging feature. Set it to 'True' to enable logging, or to 'False' to disable it. It is False by default, so you can just omit the parameter if you don't need logging. The log file is located at (name of file).log.txt. Each file gets a seperate log file. **Enabling logging could be a security vulnerabilty depending on what data you're storing.**

**From there you can set values**
```
>>> file.setValue("username", "nfoert")
True
```
The first parameter is the key. The second parameter is the value. This returns True if the value was written, otherwise it throws a UnableToSetValue exception.
You can set more than one value per file. Just use different keys, or you'll overwrite the last entry.

**After you set a value, you can get it.**
```
>>> get = file.getValue("username")
>>> print(get)
"nfoert"
```
You can use `.getValue` for any key in your file.

**You can also remove a key from the file.**
```
>>> file.removeKey("username")
[fileName] Removed key 'username'
```

**The full example**
```
from jade_config import config

file = config.Config("test", True)
file.setValue("username", "nfoert")
get = file.getValue("username")
print(get)

file.removeKey("username")
```

## Future updates
<hr>

<ul>
  <li>CLI Support</li>
  <li>The ability to choose the file location (may need to use a different library than shelve.)</li>
</ul>

**Warning: The files created by this library can still be read by others, eg. hackers, by using Jade Config, shelve or others. Don't store sensitive data like passwords or API Keys! It's certainly more secure than text files, but be careful!**

## Changelog
<hr>

- [1.1.1] [5/23/23] Made errors more descriptive, added `removeKey()`, and made the database correctly close after it's done being used.
- [1.0.1] Patch fixing a small logging confusion
- [1.0.0] Initial release
