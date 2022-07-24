set -e

# Process the regression data to calculate distances to where a regression is 
# relative to its surrounding tags

./analyse-bisect.py results/c/ stats/c/commits.json commits
./analyse-bisect.py results/c++/ stats/c++/commits.json commits
./analyse-bisect.py results/c-sharp/ stats/c-sharp/commits.json commits
./analyse-bisect.py results/go/ stats/go/commits.json commits
./analyse-bisect.py results/java/ stats/java/commits.json commits
./analyse-bisect.py results/javascript/ stats/javascript/commits.json commits
./analyse-bisect.py results/objective-c/ stats/objective-c/commits.json commits
./analyse-bisect.py results/perl/ stats/perl/commits.json commits
./analyse-bisect.py results/php/ stats/php/commits.json commits
./analyse-bisect.py results/python/ stats/python/commits.json commits
./analyse-bisect.py results/r/ stats/r/commits.json commits
./analyse-bisect.py results/ruby/ stats/ruby/commits.json commits
./analyse-bisect.py results/rust/ stats/rust/commits.json commits
./analyse-bisect.py results/swift/ stats/swift/commits.json commits

# Apply the regression algorithm to the commit data to fit a curve to the 
# distribution of normalised regression locations

./regression-nfold.py stats/c/commits.json
./regression-nfold.py stats/c/lines.json
./regression-nfold.py stats/c/blocks.json
./regression-nfold.py stats/c++/commits.json
./regression-nfold.py stats/c++/lines.json
./regression-nfold.py stats/c++/blocks.json
./regression-nfold.py stats/c-sharp/commits.json
./regression-nfold.py stats/c-sharp/lines.json
./regression-nfold.py stats/c-sharp/blocks.json
./regression-nfold.py stats/go/commits.json
./regression-nfold.py stats/go/lines.json
./regression-nfold.py stats/go/blocks.json
./regression-nfold.py stats/java/commits.json
./regression-nfold.py stats/java/lines.json
./regression-nfold.py stats/java/blocks.json
./regression-nfold.py stats/javascript/commits.json
./regression-nfold.py stats/javascript/lines.json
./regression-nfold.py stats/javascript/blocks.json
./regression-nfold.py stats/objective-c/commits.json
./regression-nfold.py stats/objective-c/lines.json
./regression-nfold.py stats/objective-c/blocks.json
./regression-nfold.py stats/perl/commits.json
./regression-nfold.py stats/perl/lines.json
./regression-nfold.py stats/perl/blocks.json
./regression-nfold.py stats/php/commits.json
./regression-nfold.py stats/php/lines.json
./regression-nfold.py stats/php/blocks.json
./regression-nfold.py stats/python/commits.json
./regression-nfold.py stats/python/lines.json
./regression-nfold.py stats/python/blocks.json
./regression-nfold.py stats/r/commits.json
./regression-nfold.py stats/r/lines.json
./regression-nfold.py stats/r/blocks.json
./regression-nfold.py stats/ruby/commits.json
./regression-nfold.py stats/ruby/lines.json
./regression-nfold.py stats/ruby/blocks.json
./regression-nfold.py stats/rust/commits.json
./regression-nfold.py stats/rust/lines.json
./regression-nfold.py stats/rust/blocks.json
./regression-nfold.py stats/swift/commits.json
./regression-nfold.py stats/swift/lines.json
./regression-nfold.py stats/swift/blocks.json

# Apply the bisect algorithm to calculate the number of steps needed to detect 
# the regression commit using different distance metrics

./analyse-bisect.py results/c/ stats/c/commits-weighted.json commits 10.62988956267997 -95.85165636436697 91.51799274623352
./analyse-bisect.py results/c/ stats/c/lines-weighted.json lines 11.080415518301999 -124.71439313216983 120.23301484877652
./analyse-bisect.py results/c/ stats/c/blocks-weighted.json blocks 10.872833015656356 -110.3757504329785 105.9173162006048

./analyse-bisect.py results/c++/ stats/c++/commits-weighted.json commits 8.539698676520223 -100.19762606253131 -1269.0768358804728
./analyse-bisect.py results/c++/ stats/c++/lines-weighted.json lines 9.680710305907606 -189.72118789852618 -1075.7559339489649
./analyse-bisect.py results/c++/ stats/c++/blocks-weighted.json blocks 9.176859306453453 -149.67026428491783 -1052.5814170760393

./analyse-bisect.py results/c-sharp/ stats/c-sharp/commits-weighted.json commits 7.367933535910531 -139.70798637211857 26.12215933587633
./analyse-bisect.py results/c-sharp/ stats/c-sharp/lines-weighted.json lines 8.327462511929962 -205.43652944998917 -411.94155630565336
./analyse-bisect.py results/c-sharp/ stats/c-sharp/blocks-weighted.json blocks 7.940909891005273 -178.43669633735286 -446.1463864570749

./analyse-bisect.py results/go/ stats/go/commits-weighted.json commits 2.504153188007941 -24.24229667864376 11.081153075422854
./analyse-bisect.py results/go/ stats/go/lines-weighted.json lines 3.395405279838266 -46.89415362784415 5.10311172243283
./analyse-bisect.py results/go/ stats/go/blocks-weighted.json blocks 2.846116058103056 -34.15172897798313 11.541639171798428

./analyse-bisect.py results/java/ stats/java/commits-weighted.json commits 9.500077378482331 -22.033996714601308 -5770.389530334999
./analyse-bisect.py results/java/ stats/java/lines-weighted.json lines 11.086622895391429 -229.18802861562125 210.03348522291688
./analyse-bisect.py results/java/ stats/java/blocks-weighted.json blocks 9.551822133764727 -13.795740373692762 -6607.200167143314

./analyse-bisect.py results/javascript/ stats/javascript/commits-weighted.json commits 3.4693341785928613 -37.068340865560586 7.966561834987702
./analyse-bisect.py results/javascript/ stats/javascript/lines-weighted.json lines 5.483672794463211 -139.0493685756423 9.077651467976724
./analyse-bisect.py results/javascript/ stats/javascript/blocks-weighted.json blocks 4.303355538357157 -69.42020837378702 19.64189170888161

./analyse-bisect.py results/objective-c/ stats/objective-c/commits-weighted.json commits 3.261293355536825 -27.027305026951947 -5.267090426159255
./analyse-bisect.py results/objective-c/ stats/objective-c/lines-weighted.json lines 5.464816419174688 -137.0541374733456 8.693408028143384
./analyse-bisect.py results/objective-c/ stats/objective-c/blocks-weighted.json blocks 4.0584430337377055 -54.707807289966546 7.043970293610352

./analyse-bisect.py results/perl/ stats/perl/commits-weighted.json commits 4.383517536041742 -73.9549576752065 21.40912540501205
./analyse-bisect.py results/perl/ stats/perl/lines-weighted.json lines 4.561664509130211 -82.64012301725334 21.89390687791949
./analyse-bisect.py results/perl/ stats/perl/blocks-weighted.json blocks 4.528739033650077 -81.53378318178615 24.669098846771252

./analyse-bisect.py results/php/ stats/php/commits-weighted.json commits 6.644974269510799 -142.96729233445456 6.977144026431489
./analyse-bisect.py results/php/ stats/php/lines-weighted.json lines 6.8386000993656175 -149.39022509258993 33.323225788105596
./analyse-bisect.py results/php/ stats/php/blocks-weighted.json blocks 6.621020468144531 -136.11145916019197 37.82801736896682

./analyse-bisect.py results/python/ stats/python/commits-weighted.json commits 7.931497531909674 -169.50410167799623 26.72340375285933
./analyse-bisect.py results/python/ stats/python/lines-weighted.json lines 8.783894825357855 -234.30865836795758 44.073441986095126
./analyse-bisect.py results/python/ stats/python/blocks-weighted.json blocks 7.941253518637688 -164.54782960086644 48.328045467214025

./analyse-bisect.py results/r/ stats/r/commits-weighted.json commits 3.250197882466596 -31.849555537202836 7.668411902988024
./analyse-bisect.py results/r/ stats/r/lines-weighted.json lines 3.97257555275754 -55.610972081135685 10.358176881868742
./analyse-bisect.py results/r/ stats/r/blocks-weighted.json blocks 3.5095604284514352 -40.6574399838293 8.236738249612374

./analyse-bisect.py results/ruby/ stats/ruby/commits-weighted.json commits 3.2650357794861575 -35.16169489129629 7.713734855501081
./analyse-bisect.py results/ruby/ stats/ruby/lines-weighted.json lines 3.8652486178232226 -55.07205443821917 19.889838935759286
./analyse-bisect.py results/ruby/ stats/ruby/blocks-weighted.json blocks 3.551165002401074 -45.8997265256423 16.65493116475988

./analyse-bisect.py results/rust/ stats/rust/commits-weighted.json commits 5.219095336558027 -105.55778465013502 17.82413495924007
./analyse-bisect.py results/rust/ stats/rust/lines-weighted.json lines 6.4238186297548525 -188.33280515743573 15.476516875896433
./analyse-bisect.py results/rust/ stats/rust/blocks-weighted.json blocks 5.7283302983901345 -139.14035957973698 -4.64506921092859

./analyse-bisect.py results/swift/ stats/swift/commits-weighted.json commits 1.708469572238356 -9.825429908357751 -11.369284241051943
./analyse-bisect.py results/swift/ stats/swift/lines-weighted.json lines 3.1369160670434337 -39.7035913913922 -4.341401108300585
./analyse-bisect.py results/swift/ stats/swift/blocks-weighted.json blocks 2.520447172031918 -24.165744078878244 0.60024993523691

# Generate graphs from the data for inclusion in the writeup

./graphs.py stats/c/ writeup/figures/
./graphs.py stats/javascript/ writeup/figures/ 10


