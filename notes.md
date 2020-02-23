# Find reverts
git log --format="%H" --grep "revert"

# Show commit for tag
git show --format="%H" 1.8.2 | head -1
git rev-list -n 1 1.8.2

# List latest tag before
git tag --contains dcda2c6 --sort=committerdate | head -1
git describe --tag dcda2c6

# List earliest tag after
git tag --no-contains dcda2c6 --sort=committerdate | tail -1
git describe --tag --contains dcda2c6

# Earliest commit
git rev-list --max-parents=0 HEAD

# Latest commit
HEAD

# Commit revert refers to
$r = `git log --format="%b" $i | grep -o -E "[0-9a-f]{7}|[0-9a-f]{40}"`


Format <tag_before> <reverted> <reverting> <tag_after>

for i in `git log --format="%H" --grep "revert"`; do r=`git log --format="%b" -1 $i | grep -o -E "[0-9a-f]{7}|[0-9a-f]{40}"`; if [ -n "$r" ]; then before=`git describe --tag --first-parent --abbrev=0 $r 2>/dev/null | cut -f1 -d"~"`; after=`git describe --tag --first-parent --abbrev=0 --contains $r 2>/dev/null | cut -f1 -d"~"`; below=`[ -z "$before" ] && echo \`git rev-list --max-parents=0 HEAD\` || echo $before`; above=`[ -z "$after" ] && echo "HEAD" || echo $after`; echo `git rev-list -n 1 $below` $r $i `git rev-list -n 1 $above`; fi; done




for i in `git log --format="%H" --grep "revert"`; do
	r=`git log --format="%b" -1 $i | grep -o -E "[0-9a-f]{7}|[0-9a-f]{40}"`
	if [ -n "$r" ]; then
		before=`git describe --tag --first-parent --abbrev=0 $r 2>/dev/null | cut -f1 -d"~"`
		after=`git describe --tag --first-parent --abbrev=0 --contains $r 2>/dev/null | cut -f1 -d"~"`
		below=`[ -z "$before" ] && echo \`git rev-list --max-parents=0 HEAD\` || echo $before`
		above=`[ -z "$after" ] && echo "HEAD" || echo $after`
		echo `git rev-list -n 1 $below` $r $i `git rev-list -n 1 $above`
	fi
done

