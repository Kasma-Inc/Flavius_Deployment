{{/*
Helper functions to convert Kubernetes resource values for ConfigMap usage.
- Memory: Converts Ki/Mi/Gi/Ti/Pi/Ei/B to integer bytes.
- CPU: Convert CPU notation (m or cores) into integer cores. Automatically rounds up any fractional core to the next integer.
*/}}

{{- define "flavius.toBytes" -}}
{{- /* 获取输入值，转换为字符串，转换为小写，然后移除所有空白字符 */ -}}
{{- $mem := . | toString | lower | trim -}}
{{- if hasSuffix "ei" $mem -}}
{{- mul (trimSuffix "ei" $mem) 1152921504606846976 -}}
{{- else if hasSuffix "pi" $mem -}}
{{- mul (trimSuffix "pi" $mem) 1125899906842624 -}}
{{- else if hasSuffix "ti" $mem -}}
{{- mul (trimSuffix "ti" $mem) 1099511627776 -}}
{{- else if hasSuffix "gi" $mem -}}
{{- mul (trimSuffix "gi" $mem) 1073741824 -}}
{{- else if hasSuffix "mi" $mem -}}
{{- mul (trimSuffix "mi" $mem) 1048576 -}}
{{- else if hasSuffix "ki" $mem -}}
{{- mul (trimSuffix "ki" $mem) 1024 -}}
{{- else if hasSuffix "b" $mem -}}
{{- trimSuffix "b" $mem -}}
{{- else if regexMatch "^[0-9]+$" $mem -}}
{{- $mem -}}
{{- else -}}
{{- fail (printf "Unsupported memory unit in value: %s (must be Ki/Mi/Gi/Ti/Pi/Ei/B or plain integer bytes)" .) -}}
{{- end -}}
{{- end -}}

{{- define "flavius.toCores" -}}
{{- $cpu := . | toString | lower | trim -}}
{{- if hasSuffix "m" $cpu -}}
  {{- $milli := trimSuffix "m" $cpu | int -}}
  {{- div (add $milli 999) 1000 -}}
{{- else if regexMatch "^[0-9]+\\.?[0-9]*$" $cpu -}}
  {{- $val := $cpu | float64 -}}
  {{- if lt $val 1.0 -}}
    1
  {{- else -}}
    {{- ceil $val | int -}}
  {{- end -}}
{{- else -}}
  {{- fail (printf "Unsupported CPU unit in value: '%s'" .) -}}
{{- end -}}
{{- end -}}

{{/*
Calculate max_memory_pool_bytes:
- memoryStr: input like "2Gi", "2048Mi"
- logic: max_pool = memory * 0.85 - 1GB
- minimum 1GB
*/}}
{{- define "flavius.calcMaxMemoryPool" -}}
{{- $memoryStr := . -}}
{{- /* convert memory string to bytes */ -}}
{{- $memBytes := include "flavius.toBytes" $memoryStr | float64 -}}
{{- /* multiply by 0.85 */ -}}
{{- $scaled := mulf $memBytes 0.85 -}}
{{- /* subtract 1GB */ -}}
{{- $c := subf $scaled 1073741824 -}}
{{- /* enforce minimum 1GB */ -}}
{{- if lt $c 1073741824.0 -}}
1073741824
{{- else -}}
{{- printf "%.0f" $c -}}
{{- end -}}
{{- end -}}
