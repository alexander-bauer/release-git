# release
### make git releases automatically

**release** is a git release-generating tool. It obeys semantic
versioning, and uses keywords in order to advance the version. For
example, *release minor* on a project whose most recent tag is
*v0.2.1*, a new tag will be made with the label *v0.3.0* and the
message being a changelog of all items between the new tag and
*v0.2.0*. It is also capable of handling prerelease labels.

Versions tags are always of the following form:
v**major**.**minor**.**patch***[-**prerelease**]*.

These correspond to the specification for semantic versioning, in
which *major* refers to non-backwards compatible versions of the
public API, *minor* refers to backwards compatible feature additions
and deprications (but not removals), *patch* refers to bugfixes and
minor changes, and *prerelease* is an optionally supplied (with a dash
(\-) separating it from the version if so) string, such as "alpha", or
"rc2". See full specification at <http://semver.org>.

Full documentation is available as a manpage, either on
[GitHub][manpage] or once installed via `man release`.

## Author and Copyright

Copyright (C) 2014 Alexander Bauer

License GPLv3+: GNU GPL version 3
or later <http://gnu.org/licenses/gpl.html>.  
This is free software: you are free to change and redistribute it.
There is NO WARRANTY, to the extent permitted by law.

Bug reports and feature requests are *greatly* appreciated, and should
both be made to the [issues][] page, or to the author, Alexander Bauer
<sasha@crofter.org>.

[manpage]: https://github.com/SashaCrofter/release-git/blob/master/doc/release.1
[issues]: https://github.com/SashaCrofter/release-git/issues
