# remove .pyc files since saecloud's svn doesn't ignore them
for f in `ls -R | grep \.pyc$`
do
	rm -I -v "$f"
done

