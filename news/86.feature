``i18ndude rebuild-pot --exclude="name1 name2"`` now also accepts directory names for exclusion.
Excluding a directory name will exclude all files in and below the given directory,
but only if the directory name exactly matches a exclusion name (no globs, no substring match).
This change now also results in the hardcoded exclusions for 'tests' and 'docs' to actually work.
