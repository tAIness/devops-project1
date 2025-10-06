{{- define "apps.targetRevision" -}}
{{- if .Values.global.targetRevision -}}
{{ .Values.global.targetRevision }}
{{- else -}}
{{ .Chart.AppVersion }}
{{- end -}}
{{- end }}

{{- define "apps.imageTag" -}}
{{- if .Values.global.appImageTag -}}
{{ .Values.global.appImageTag }}
{{- else -}}
{{ .Chart.AppVersion }}
{{- end -}}
{{- end }}
