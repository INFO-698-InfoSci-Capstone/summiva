class Document {
  final int id;
  final String title;
  final String content;
  final int userId;

  Document({
    required this.id,
    required this.title,
    required this.content,
    required this.userId
  });

  factory Document.fromJson(Map<String, dynamic> json) {
    return Document(
      id: json['id'],
      title: json['title'],
      content: json['content'],
      userId: json['user_id']
    );
  }

  Map<String, dynamic> toJson() => {
    'id': id,
    'title': title,
    'content': content,
    'user_id': userId
  };
}