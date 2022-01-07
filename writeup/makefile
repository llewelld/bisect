all: paper.pdf

bisect.aux: bisect.tex bisect.bib
	pdflatex bisect.tex

bisect.bbl: bisect.aux
	bibtex bisect.aux

bisect.pdf: bisect.tex bisect.bbl
	pdflatex bisect.tex
	pdflatex bisect.tex

paper.pdf: bisect.pdf
	cp bisect.pdf paper.pdf

clean:
	rm *.blg *.log *.pdf *.bbl *.aux *.out *.wiki

