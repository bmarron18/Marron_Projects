

#############
pyreport
##############
http://gael-varoquaux.info/programming/pyreport-literate-programming-in-python.html
https://answers.launchpad.net/pyreport/+question/50479
https://itb.biologie.hu-berlin.de/~bergmann/pyreporttips.html

	#This is the original script already made executable
	#if needed 
	
	a.  move pyreport folder to /home/bmarron/anaconda2/pkgs



	#already done	
	b.  make the file executable
/home/bmarron/anaconda2/pkgs/pyreport/chmod uog+x pyreport.py	

	c. add this to .bashrc
export PATH="/home/bmarron/anaconda2/pkgs/pyreport:$PATH"



	#to use
	d. use pyreport.py -x file.py
	
	e. test
$ pyreport.py -h
	
	f example
$ pyreport.py -x ~/Desktop/test.py
Outputing report to /home/bmarron/Desktop/test.pdf
Compiling document to pdf
Ran script in 1.37s

	g. runs on .txt files, too!


	
