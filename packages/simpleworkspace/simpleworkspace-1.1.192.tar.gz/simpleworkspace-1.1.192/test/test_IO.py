import hashlib
import os
import simpleworkspace as sw
from simpleworkspace.io.file import FileInfo
from basetestcase import BaseTestCase
import tempfile


class IO_FileTests(BaseTestCase):
    class _tmpNestedFolderInfo():
        SubEntriesCount = 0
        SubDirCount = 0
        FileCount = 0
        FileOfTypeTextCount = 0
        FileOfTypeTextContent = ''
        FileOfTypeBinaryCount = 0
        FileOfTypeBinaryContent = b''
        totalFileSize = 0
        entryPath = ""

    def _tmpNestedFolder(self):
        nestedInfo = self._tmpNestedFolderInfo()
        nestedInfo.entryPath = self.tmpDir("nested")
        nestedInfo.FileOfTypeBinaryContent = b"\x00\x01\x02\x03\x04\x05\x06\x07\x08\x09"
        nestedInfo.FileOfTypeTextContent = "1234567890"

        self.tmpDir(f"./nested/a1")
        self.tmpFile("nested/a1/file1.txt", nestedInfo.FileOfTypeTextContent)
        self.tmpFile("nested/a1/file2.txt", nestedInfo.FileOfTypeTextContent)
        self.tmpFile("nested/a1/file3.bin",  nestedInfo.FileOfTypeBinaryContent)
        self.tmpDir(f"./nested/a1/a2")
        self.tmpDir(f"./nested/a1/a2/a3")
        self.tmpDir(f"./nested/b1")
        self.tmpDir(f"./nested/c1/a2")
        self.tmpDir(f"./nested/c1/b2")
        self.tmpDir(f"./nested/c1/c2")
        self.tmpDir(f"./nested/c1/c2/c3")
        self.tmpDir(f"./nested/c1/c2/c3/c4")
        self.tmpFile("nested/c1/c2/c3/c4/file1.txt", nestedInfo.FileOfTypeTextContent)
        self.tmpFile("nested/c1/c2/c3/c4/file2.bin",  nestedInfo.FileOfTypeBinaryContent)
        nestedInfo.SubDirCount = 10
        nestedInfo.FileOfTypeBinaryCount = 2
        nestedInfo.FileOfTypeTextCount = 3
        nestedInfo.FileCount = nestedInfo.FileOfTypeBinaryCount + nestedInfo.FileOfTypeTextCount
        nestedInfo.totalFileSize = len(nestedInfo.FileOfTypeBinaryContent) * nestedInfo.FileOfTypeBinaryCount + len(nestedInfo.FileOfTypeTextContent) * nestedInfo.FileOfTypeTextCount
        nestedInfo.SubEntriesCount = nestedInfo.SubDirCount + nestedInfo.FileCount
        return nestedInfo

    def test_FileContainer_GetsValidPaths(self):
        t0 = FileInfo("a/b/c.exe")
        t1 = FileInfo("a/b/c")
        t2 = FileInfo("a/b/.exe")
        t3 = FileInfo(".exe")
        t4 = FileInfo("c")
        t5 = FileInfo("c.exe")
        t6 = FileInfo(".")
        t7 = FileInfo("a.,-.asd/\\/b.,ca.asd/c.,..exe")
        
        self.assertTrue(t0.FileExtension == "exe" and t0.Filename == "c"    and t0.Tail == "a/b"                   and t0.Head == "c.exe"     )
        self.assertTrue(t1.FileExtension == ""    and t1.Filename == "c"    and t1.Tail == "a/b"                   and t1.Head == "c"         )
        self.assertTrue(t2.FileExtension == "exe" and t2.Filename == ""     and t2.Tail == "a/b"                   and t2.Head == ".exe"      )
        self.assertTrue(t3.FileExtension == "exe" and t3.Filename == ""     and t3.Tail == ""                       and t3.Head == ".exe"     )
        self.assertTrue(t4.FileExtension == ""    and t4.Filename == "c"    and t4.Tail == ""                       and t4.Head == "c"        )
        self.assertTrue(t5.FileExtension == "exe" and t5.Filename == "c"    and t5.Tail == ""                       and t5.Head == "c.exe"    )
        self.assertTrue(t6.FileExtension == ""    and t6.Filename == ""     and t6.Tail == ""                       and t6.Head == "."        )
        self.assertTrue(t7.FileExtension == "exe" and t7.Filename == "c.,." and t7.Tail == "a.,-.asd///b.,ca.asd"  and t7.Head == "c.,..exe"  )

        t8 = FileInfo("a/b/c")
        self.assertTrue(t8.Tail == "a/b" and t8.Head == "c")
        self.assertEqual(t8.Parent.Tail == "a", t8.Parent.Head == "b")
        return

    def test_FileContainer_UsesCaching(self):
        t0 = FileInfo("a/b/c.exe")
        self.assertTrue(t0.Filename is t0.Filename)
        self.assertTrue(t0.FileExtension is t0.FileExtension)
        self.assertTrue(t0.Tail is t0.Tail)
        self.assertTrue(t0.Head is t0.Head)
        self.assertTrue(t0.RealPath is t0.RealPath)
        self.assertTrue(t0._HeadTail is t0._HeadTail)
        self.assertTrue(t0._FilenameSplit is t0._FilenameSplit)
        return
    
    def test_File_ReadsCorrectTypes(self):
        f1 = self.tmpFile("file1.txt", "1234567890")
            
        data = sw.io.file.Read(f1)
        self.assertIs(type(data), str)
        data = sw.io.file.Read(f1, callback=lambda x: self.assertEqual(type(x), str))
        self.assertIs(data, None)

        ##bytes##
        data = sw.io.file.Read(f1, getBytes=True)
        self.assertIs(type(data), bytes)
        data = sw.io.file.Read(f1, callback=lambda x: self.assertEqual(type(x), bytes), getBytes=True)
        self.assertIs(data, None)
    def test_File_Reading_ReadsCorrect(self):
        #empty file test
        f1 = self.tmpFile("empty.txt", "")
        self.assertEqual(sw.io.file.Read(f1), "")

        #simple reads
        fileContent = "1234567890"
        f1 = self.tmpFile("file1.txt", fileContent)
        result = sw.io.file.Read(f1, readLimit=len(fileContent))
        self.assertEqual(result,  fileContent)
        dataBytes = sw.io.file.Read(f1, readLimit=len(fileContent), getBytes=True)
        self.assertEqual(dataBytes,  fileContent.encode())

        #scenario readsize larger than filesize
        result = sw.io.file.Read(f1, readSize=100)
        self.assertEqual(result, "1234567890")


        # scenario has readSize and readlimit
        result = []
        sw.io.file.Read(f1, callback=result.append, readSize=2, readLimit=6)
        self.assertEqual(result, ["12", "34", "56"])
        
        # scenerio has only readsize, should read unlimited
        result = []
        sw.io.file.Read(f1, callback=lambda x: result.append(x), readSize=2)
        self.assertEqual(
            result,
            ["12", "34", "56", "78", "90"]
        )

        #scenario has readsize bigger than readlimit, should only be able to read until readlimit
        result = []
        sw.io.file.Read(f1, callback=result.append, readSize=5, readLimit=2)
        self.assertEqual(result, ["12"])

        # scenario readsize is unlimited but readlimit is set, should only read to readlimit
        result = []
        sw.io.file.Read(f1, callback=result.append, readSize=-1, readLimit=4)
        self.assertEqual(result, ["1234"])

    def test_Hash_GetsCorrectHash(self):
        fileContent = b"\x00\x01\x02\x03\x04"
        f1 = self.tmpFile("file1.txt", fileContent)
        originalHash = sw.io.file.Hash(f1, hashFunc=hashlib.sha256())

        #
        sha256 = hashlib.sha256()
        sha256.update(fileContent)
        resultHash = sha256.hexdigest()
        self.assertEqual(originalHash,  resultHash)
        #
        sha256 = hashlib.sha256()
        sw.io.file.Read(f1, callback=sha256.update, getBytes=True)
        resultHash = sha256.hexdigest()
        self.assertEqual(originalHash,  resultHash)
        #
        sha256 = hashlib.sha256()
        sw.io.file.Read(f1, callback=sha256.update, readSize=2, getBytes=True)
        resultHash = sha256.hexdigest()
        self.assertEqual(originalHash,  resultHash)
        #
        sha256 = hashlib.sha256()
        sw.io.file.Read(f1, callback=sha256.update, readLimit=len(fileContent), getBytes=True)
        resultHash = sha256.hexdigest()
        self.assertEqual(originalHash,  resultHash)


    def test_Directories_ListsAll(self):
        nestedInfo = self._tmpNestedFolder()
        
        fileSizes = []
        sw.io.directory.List(nestedInfo.entryPath, lambda x: fileSizes.append(os.path.getsize(x)), includeDirs=False)
        self.assertEqual(sum(fileSizes),  nestedInfo.totalFileSize)

        #
        tmpList = []
        sw.io.directory.List(nestedInfo.entryPath, tmpList.append, includeDirs=False)
        self.assertEqual(len(tmpList),  nestedInfo.FileCount)

        #
        tmpList = []
        sw.io.directory.List(nestedInfo.entryPath, tmpList.append, includeDirs=True)
        self.assertEqual(len(tmpList),  nestedInfo.SubEntriesCount)
        return

    def test_Directories_ListsOnlyDirectories(self):
        nestedInfo = self._tmpNestedFolder()

        #
        tmpList = sw.io.directory.List(nestedInfo.entryPath, includeDirs=False, includeFiles=False)
        self.assertEqual(len(tmpList),  0)

        #
        tmpList = sw.io.directory.List(nestedInfo.entryPath, includeDirs=True, includeFiles=False)
        self.assertEqual(len(tmpList),  nestedInfo.SubDirCount)

    def test_Directories_ListsAll_maxDepth(self):
        nestedInfo = self._tmpNestedFolder()
        #
        level1_Entries = list(os.scandir(nestedInfo.entryPath)) 
        totalEntriesLevel1 = len(level1_Entries)

        tmpList = []
        sw.io.directory.List(nestedInfo.entryPath, tmpList.append, maxRecursionDepth=1)
        self.assertEqual(len(tmpList),  totalEntriesLevel1)

        level2_Entries = []
        totalEntriesLevel2 = totalEntriesLevel1
        for fd in level1_Entries:
            if(fd.is_dir()):
                entries = list(os.scandir(fd.path))
                level2_Entries.extend(entries)
                totalEntriesLevel2 += len(entries)

        tmpList = []
        sw.io.directory.List(nestedInfo.entryPath, tmpList.append, maxRecursionDepth=2)
        self.assertEqual(len(tmpList),  totalEntriesLevel2)

        level3_Entries = []
        totalEntriesLevel3 = totalEntriesLevel2
        for fd in level2_Entries:
            if(fd.is_dir()):
                entries = list(os.scandir(fd.path))
                level3_Entries.extend(entries)
                totalEntriesLevel3 += len(entries)
        
        tmpList = []
        sw.io.directory.List(nestedInfo.entryPath, tmpList.append, maxRecursionDepth=3)
        self.assertEqual(len(tmpList),  totalEntriesLevel3)


        tmpList = []
        sw.io.directory.List(nestedInfo.entryPath, tmpList.append, includeDirs=False, maxRecursionDepth=9999)
        self.assertEqual(len(tmpList),  nestedInfo.FileCount)

        allItems = sw.io.directory.List(nestedInfo.entryPath, maxRecursionDepth=9999)
        self.assertEqual(len(allItems),  nestedInfo.SubEntriesCount)
        return


    def test_Directories_callbackFiltering_1(self):
        nestedInfo = self._tmpNestedFolder()
        tmpList = []
        sw.io.directory.List(nestedInfo.entryPath, tmpList.append, includeFilter = lambda x: x.endswith(".txt") or x.endswith(".unkown"))
        self.assertEqual(len(tmpList), nestedInfo.FileOfTypeTextCount)
        for i in tmpList:
            fcon = FileInfo(i)
            self.assertEqual(fcon.FileExtension, "txt")
        return

    def test_Directories_regexFiltering_1(self):
        nestedInfo = self._tmpNestedFolder()

        tmpList = []
        sw.io.directory.List(nestedInfo.entryPath, tmpList.append, includeFilter=r"/\.(unkown|txt)/i")
        self.assertEqual(len(tmpList), nestedInfo.FileOfTypeTextCount)
        for i in tmpList:
            fcon = FileInfo(i)
            self.assertEqual(fcon.FileExtension, "txt")
        return

    def test_Directories_regexFiltering_2(self):
        nestedInfo = self._tmpNestedFolder()

        tmpList = []
        sw.io.directory.List(nestedInfo.entryPath, tmpList.append, includeFilter=r"/\.(bin)$/i")
        for path in tmpList:
            self.assertEqual(
                sw.io.file.Read(path, getBytes=True),
                nestedInfo.FileOfTypeBinaryContent
            )
        self.assertEqual(len(tmpList),  nestedInfo.FileOfTypeBinaryCount)

    def test_Directories_regexFiltering_3(self):
        nestedInfo = self._tmpNestedFolder()
        tmpList = []
        sw.io.directory.List(nestedInfo.entryPath, tmpList.append, includeFilter=r"/\.(unkown)$/")
        self.assertEqual(len(tmpList),  0)
        return

    def test_Directories_regexFiltering_AllFiles_1(self):
        nestedInfo = self._tmpNestedFolder()
        tmpList = []
        sw.io.directory.List(nestedInfo.entryPath, tmpList.append, includeFilter=r"/\.(bin|txt)$/")
        self.assertEqual(len(tmpList),  nestedInfo.FileCount)
        return

    def test_Directories_regexFiltering_AllFiles_2(self):
        nestedInfo = self._tmpNestedFolder()
        tmpList = []
        sw.io.directory.List(nestedInfo.entryPath, tmpList.append, includeFilter=r"/.*/i")
        self.assertEqual(len(tmpList),  nestedInfo.SubEntriesCount)


    def test_Directories_files_in_directory(self):
        tmpdir = self.tmpDir("a")
        file1 = self.tmpFile("a/file1.txt")
        file2 = self.tmpFile("a/file2.txt")
        file3 = self.tmpFile("a/file3.jpg")

        # Test listing files
        files = []
        sw.io.directory.List(tmpdir, lambda x: files.append(x))
        self.assertEqual(len(files), 3)
        self.assertIn(file1, files)
        self.assertIn(file2, files)
        self.assertIn(file3, files)

    def test_Directories_directories_in_directory(self):
        # Create a temporary directory and some subdirectories

        entryDir = self.tmpDir("a")
        subDir1 = self.tmpDir("a/dir1")
        subDir2 = self.tmpDir("a/dir2")

        # Test listing directories
        dirs = []
        sw.io.directory.List(entryDir, lambda x: dirs.append(x), includeDirs=True, includeFiles=False)
        self.assertEqual(len(dirs), 2)
        self.assertIn(subDir1, dirs)
        self.assertIn(subDir2, dirs)


    def test_Directories_include_filter(self):
        # Create a temporary directory and some files
        tmpdir = self.tmpDir("a")
        file1 = self.tmpFile("a/file1.txt")
        file2 = self.tmpFile("a/file2.txt")
        file3 = self.tmpFile("a/file3.jpg")

        # Test filtering files by extension
        files = []
        sw.io.directory.List(tmpdir, lambda x: files.append(x), includeFilter=r'/\.txt$/')
        self.assertEqual(len(files), 2)
        self.assertIn(file1, files)
        self.assertIn(file2, files)
        self.assertNotIn(file3, files)
        return
    
    def test_Directories_satisfied_condition(self):
        # Create a temporary directory and some files
        tmpdir = self.tmpDir("a1/")
        self.tmpDir("a1/a2/")
        nestedFile = self.tmpFile("a1/a2/nestedFile.txt")

        file1 = self.tmpFile("a1/file1.txt")
        file2 = self.tmpFile("a1/file2.txt")
        file3 = self.tmpFile("a1/file3.jpg")

        # Test stopping recursion early with a satisfied condition
        files = []
        sw.io.directory.List(tmpdir, lambda x: files.append(x), satisfiedCondition=lambda x: 'file2.txt' in x)
        self.assertIn(file2, files)
        self.assertNotIn(nestedFile, files)

        # Test satisfied condition with everything allowed through
        files = []
        sw.io.directory.List(tmpdir, lambda x: files.append(x), satisfiedCondition=lambda x: False)
        self.assertEqual(len(files), 5)
        self.assertIn(file1, files)
        self.assertIn(file2, files)
        self.assertIn(file3, files)
        self.assertIn(nestedFile, files)

        # Test satisfied condition with nothing allowed through
        files = []
        sw.io.directory.List(tmpdir, lambda x: files.append(x), satisfiedCondition=lambda x: True)
        self.assertEqual(len(files), 1)
        return

    def test_Directories_exception_callback(self):
        tmpdir = self.tmpDir("a")
        file1 = self.tmpFile("a/file1.txt")
        # Test handling of permission error with exception callback
        exceptions = []
        sw.io.directory.List(tmpdir, callback= lambda x: x["RaiseError"], exceptionCallback=lambda x: exceptions.append(x))
        self.assertEqual(len(exceptions), 1)
        self.assertIsInstance(exceptions[0], TypeError)


