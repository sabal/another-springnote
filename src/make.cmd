RMDIR dist /S /Q
RMDIR dist /S /Q
C:\Python27\Python.exe -OO setup.py py2exe
MOVE dist\shell.exe dist\Springnote.exe
RMDIR "Another Springnote" /S /Q
RMDIR "Another Springnote" /S /Q
MOVE dist "Another Springnote"
