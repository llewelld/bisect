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





# Build matplotlib on Sailfish OS

See:
https://github.com/nobodyinperson/matplotlib
https://openrepos.net/content/nobodyinperson/python3-matplotlib

libfreetype2 -> freetype

devel-su zypper install git gcc-c++ python3-devel freetype freetype-devel libpng-devel rpm-build
git clone git@github.com:nobodyinperson/matplotlib.git
cd matplotlib
python3 -m venv .
source bin/activate
pip install cython

python3 setup.py bdist_rpm

# More Reading

\section{More reading}

\begin{enumerate}
\item Dambros2010 page 6.
\item yan2019
\item X. Yang, D. Lo, X. Xia, Y. Zhang, and J. Sun, “Deep learning for just-in-time defect prediction,” in Software Quality, Reliability and Security (QRS), 2015 IEEE International Conference on, Aug 2015, pp. 17–26.
\item S. Kim, E. J. W. Jr., and Y. Zhang, “Classifying software changes: Clean or buggy?” IEEE Transactions on Software Engineering, vol. 34, no. 2, pp. 181–196, March 2008.
\item S. Kim, T. Zimmermann, K. Pan, and E. J. J. Whitehead, “Automatic identification of bug-introducing changes,” in Proceedings of the 21st IEEE/ACM International Conference on Automated Software Engineering, ser. ASE ’06. Washington, DC, USA: IEEE Computer Society, 2006, pp. 81–90.
\end{enumerate}

# Possible places for submission

IEEE Transactions on Software Engineering
Impact Factor: 9.322
Eigenfactor: 0.006
Open Access: $2195
https://ieeexplore.ieee.org/xpl/RecentIssue.jsp?punumber=32


IEEE Open Journal of the Computer Society
Impact Factor: n/a
Eigenfactor: n/a
Open Access: $1850
https://ieeexplore.ieee.org/xpl/RecentIssue.jsp?punumber=8782664


IEEE Transactions on Computers
Impact Factor: 3.183
Eigenfactor: 0.011
Open Access: $2195
https://ieeexplore.ieee.org/xpl/RecentIssue.jsp?punumber=12


Computing in Science & Engineering
Impact Factor: 2.152
Eigenfactor: 0.005
Open Access: $2195
https://ieeexplore.ieee.org/xpl/RecentIssue.jsp?punumber=5992


Empirical Software Engineering
Impact Factor: 3.762
Eigenfactor: 0.002
Open Access: €2190
https://www.springer.com/journal/10664
Longer articles, looks particularly relevant


Software Quality Journal
Impact Factor: 1.813
Eigenfactor: <0.001
Open Access: €2190
https://www.springer.com/journal/11219
Longer articles, looks particularly relevant


Automated Software Engineering
Impact Factor: 1.677
Eigenfactor: <0.001
Open Access: €2190
https://www.springer.com/journal/10515
Looks particularly relevant, preference for open science


Information and Software Technology
Impact Factor: 3.862
Eigenfactor: 0.004
Open Access: €2850
https://www.sciencedirect.com/journal/information-and-software-technology


Journal of Systems and Software
Impact Factor: 3.514
Eigenfactor: 0.008
Open Access: €2850
https://www.sciencedirect.com/journal/journal-of-systems-and-software
Longer articles, looks particularly relevant


Science of Computer Programming
Impact Factor: 0.995
Eigenfactor: 0.002
Open Access: €2090
https://www.sciencedirect.com/journal/science-of-computer-programming
Longer articles, looks particularly relevant


