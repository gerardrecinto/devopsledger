{{- define "devopsledger.name" -}}
{{- default .Chart.Name .Values.nameOverride | trunc 63 | trimSuffix "-" -}}
{{- end -}}

{{- define "devopsledger.fullname" -}}
{{- printf "%s-%s" .Release.Name (include "devopsledger.name" .) | trunc 63 | trimSuffix "-" -}}
{{- end -}}
