for revert in `git log --grep "This reverts commit" --pretty=format:"%H"`;
do
    # we cannot assume that the commit hash has a specific length...
    original_commits=$(git log -n1 $revert | grep -oE "This reverts commit [0-9a-f]*" |sed "s/This reverts commit //g")

    count=$(echo $original_commits |wc -l)
    if [ "$count" == "0" ]; then
        echo "WARNING: original commit not found, Revert is: $revert"
        continue
    elif [ "$count" != "1" ]; then
        echo "WARNING: multirevert"
    fi

    # sometimes the commit reverts multiple commits
    for original_commit in $original_commits; do
        commit_before_revert=$(git log --pretty=format:"%H" -n2 $revert | tail -n1)

        tag=$(git tag --no-contains $original_commit --sort=-creatordate |head -n1)

       echo "Revert: $revert, Commit before revert: $commit_before_revert, Original commit: $original_commit, First tag before original commit: $tag"
    done
done
