class IntegrationItemModel {
  final String id;
  final String name;
  final String provider;
  final String version;
  final String description;
  final String riskLevel;
  final String healthStatus;
  final bool isConnected;

  IntegrationItemModel({
    required this.id,
    required this.name,
    required this.provider,
    required this.version,
    required this.description,
    required this.riskLevel,
    required this.healthStatus,
    required this.isConnected,
  });

  factory IntegrationItemModel.fromJson(Map<String, dynamic> json) {
    return IntegrationItemModel(
      id: json['id'] ?? '',
      name: json['name'] ?? '',
      provider: json['provider'] ?? '',
      version: json['version'] ?? '1.0.0',
      description: json['description'] ?? '',
      riskLevel: json['risk_level'] ?? 'LOW',
      healthStatus: json['health_status'] ?? 'CONNECTED',
      isConnected: json['is_connected'] ?? false,
    );
  }
}
