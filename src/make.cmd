RMDIR dist /S /Q
RMDIR dist /S /Q
C:\Python27\Python.exe -OO setup.py py2exe
MOVE dist\shell.exe dist\Springnote.exe
RMDIR "Another Springnote" /S /Q
RMDIR "Another Springnote" /S /Q
MOVE dist "Another Springnote"

SET /P VERSION= < "Another Springnote/VERSION"
"C:\Program Files\7-Zip\7z.exe" a -tzip -mx=9 "another-springnote-win32-%VERSION%-ko.zip" "Another Springnote"