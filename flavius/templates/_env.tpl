{{- define "common.env" -}}
- name: POD_IP
  valueFrom:
    fieldRef:
      fieldPath: status.podIP
- name: ETCD_ENDPOINT
  value: {{ .Values.common.etcd_endpoints | join "," }}
- name: ROOT_DIR
  value: {{ .Values.common.root_dir }}
- name: CATALOG_NAME
  value: {{ .Values.common.catalog_name }}
- name: AWS_ACCESS_KEY_ID
  value: {{ .Values.common.aws_access_key_id }}
- name: AWS_SECRET_ACCESS_KEY
  value: {{ .Values.common.aws_secret_access_key }}
- name: AWS_REGION
  value: {{ .Values.common.aws_region }}
- name: AWS_ENDPOINT
  value: {{ .Values.common.aws_endpoint }}
- name: OTLP_HTTP_URL
  value: {{ .Values.common.otlp_http_url }}
{{- end -}}