import 'dart:io';
import 'package:path/path.dart' as path;
import '../utils/path_config.dart';

class FileService {
  static final FileService _instance = FileService._internal();
  late PathConfig _pathConfig;

  factory FileService() {
    return _instance;
  }

  FileService._internal();

  Future<void> initialize() async {
    _pathConfig = await PathConfig.getInstance();
  }

  Future<String> getAppPath(String relativePath) async {
    await initialize();
    return _pathConfig.getPath(relativePath);
  }

  Future<String> getCachePath(String relativePath) async {
    await initialize();
    return _pathConfig.getCachePath(relativePath);
  }

  Future<String> getDocumentPath(String relativePath) async {
    await initialize();
    return _pathConfig.getDocumentPath(relativePath);
  }

  Future<void> ensureDirectoryExists(String dirPath) async {
    await initialize();
    await _pathConfig.ensureDirectoryExists(dirPath);
  }

  Future<File> getFile(String relativePath) async {
    final filePath = await getAppPath(relativePath);
    return File(filePath);
  }

  Future<Directory> getDirectory(String relativePath) async {
    final dirPath = await getAppPath(relativePath);
    await ensureDirectoryExists(dirPath);
    return Directory(dirPath);
  }

  Future<bool> fileExists(String relativePath) async {
    final filePath = await getAppPath(relativePath);
    return await File(filePath).exists();
  }

  Future<bool> directoryExists(String relativePath) async {
    final dirPath = await getAppPath(relativePath);
    return await Directory(dirPath).exists();
  }

  Future<void> deleteFile(String relativePath) async {
    final filePath = await getAppPath(relativePath);
    final file = File(filePath);
    if (await file.exists()) {
      await file.delete();
    }
  }

  Future<void> deleteDirectory(String relativePath) async {
    final dirPath = await getAppPath(relativePath);
    final directory = Directory(dirPath);
    if (await directory.exists()) {
      await directory.delete(recursive: true);
    }
  }
} 