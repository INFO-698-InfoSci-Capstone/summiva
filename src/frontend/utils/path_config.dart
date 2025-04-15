import 'dart:io';
import 'package:path/path.dart' as path;
import 'package:path_provider/path_provider.dart';

class PathConfig {
  static PathConfig? _instance;
  late Directory _appDir;
  late Directory _cacheDir;
  late Directory _documentsDir;

  PathConfig._();

  static Future<PathConfig> getInstance() async {
    if (_instance == null) {
      _instance = PathConfig._();
      await _instance!._initialize();
    }
    return _instance!;
  }

  Future<void> _initialize() async {
    _appDir = await getApplicationDocumentsDirectory();
    _cacheDir = await getTemporaryDirectory();
    _documentsDir = await getApplicationDocumentsDirectory();
  }

  String get appPath => _appDir.path;
  String get cachePath => _cacheDir.path;
  String get documentsPath => _documentsDir.path;

  String getPath(String relativePath) {
    return path.join(_appDir.path, relativePath);
  }

  String getCachePath(String relativePath) {
    return path.join(_cacheDir.path, relativePath);
  }

  String getDocumentPath(String relativePath) {
    return path.join(_documentsDir.path, relativePath);
  }

  Future<void> ensureDirectoryExists(String dirPath) async {
    final directory = Directory(dirPath);
    if (!await directory.exists()) {
      await directory.create(recursive: true);
    }
  }

  String normalizePath(String filePath) {
    return path.normalize(filePath);
  }

  bool isPathValid(String filePath) {
    try {
      return path.isAbsolute(filePath) || path.isRelative(filePath);
    } catch (_) {
      return false;
    }
  }
} 