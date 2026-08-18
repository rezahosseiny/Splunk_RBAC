# Source, sourcetype, and index remediation map

Legacy values as they exist in production, mapped to the governed
values the strategy requires. This is the work list for bringing the
real estate into conformance — each row is an input-layer change.

Ephemeral fragments are collapsed into patterns (`{guid}`,
`{timestamp}`, `{digits}`, `{hash}`): the pattern is what gets fixed,
and collapsing keeps per-run identifiers out of this document.

Generated from `sample_data/Splunk_Sample_data.csv` by `tools/resolve_mapping.py`.
Rows: 698.

| legacy index | legacy sourcetype | legacy source | governed index | governed sourcetype | governed source |
|---|---|---|---|---|---|
| `arista` | `arista_switch_log` | `udp:5012` | `ops_non_inf_ndl_m` | `arista:switch:syslog` | `net:arista:switch:syslog` |
| `aruba` | `aruba` | `udp:5010` | `ops_non_inf_wls_m` | `aruba:wireless:system` | `net:aruba:wireless:syslog` |
| `aruba` | `aruba:amon_sender_proc` | `udp:5010` | `ops_non_inf_wls_m` | `aruba:wireless:amon_sender_proc` | `net:aruba:wireless:syslog` |
| `aruba` | `aruba:authmgr` | `udp:5010` | `ops_non_inf_wls_m` | `aruba:wireless:authmgr` | `net:aruba:wireless:syslog` |
| `aruba` | `aruba:ble_relay` | `udp:5010` | `ops_non_inf_wls_m` | `aruba:wireless:ble_relay` | `net:aruba:wireless:syslog` |
| `aruba` | `aruba:dropbear` | `udp:5010` | `ops_non_inf_wls_m` | `aruba:wireless:dropbear` | `net:aruba:wireless:syslog` |
| `aruba` | `aruba:fpapps` | `udp:5010` | `ops_non_inf_wls_m` | `aruba:wireless:fpapps` | `net:aruba:wireless:syslog` |
| `aruba` | `aruba:isakmpd` | `udp:5010` | `ops_non_inf_wls_m` | `aruba:wireless:isakmpd` | `net:aruba:wireless:syslog` |
| `aruba` | `aruba:kernel` | `udp:5010` | `ops_non_inf_wls_m` | `aruba:wireless:kernel` | `net:aruba:wireless:syslog` |
| `aruba` | `aruba:mini_httpd` | `udp:5010` | `ops_non_inf_wls_m` | `aruba:wireless:mini_httpd` | `net:aruba:wireless:syslog` |
| `aruba` | `aruba:nanny` | `udp:5010` | `ops_non_inf_wls_m` | `aruba:wireless:nanny` | `net:aruba:wireless:syslog` |
| `aruba` | `aruba:ofald` | `udp:5010` | `ops_non_inf_wls_m` | `aruba:wireless:ofald` | `net:aruba:wireless:syslog` |
| `aruba` | `aruba:sapd` | `udp:5010` | `ops_non_inf_wls_m` | `aruba:wireless:sapd` | `net:aruba:wireless:syslog` |
| `aruba` | `aruba:snmp` | `udp:5010` | `ops_non_inf_wls_m` | `aruba:wireless:snmp` | `net:aruba:wireless:syslog` |
| `aruba` | `aruba:stm` | `udp:5010` | `ops_non_inf_wls_m` | `aruba:wireless:stm` | `net:aruba:wireless:syslog` |
| `aruba` | `aruba:wl` | `udp:5010` | `ops_non_inf_wls_m` | `aruba:wireless:wl` | `net:aruba:wireless:syslog` |
| `azure` | `ms:defender:eventhub` | `eventhub://{host}/defenderhub;` | `res_non_sec_edr_l` | `microsoft:defender:eventhub` | `api:azure:eventhub:defender` |
| `azure_ad` | `azure:aad:audit` | `ms_aad_audit:tenant_id:{guid}` | `res_non_sec_iam_aad_l` | `azure:aad:audit` | `api:azure:aad:audit` |
| `azure_ad` | `azure:aad:device` | `ms_aad_device:tenant_id:{guid}` | `res_non_sec_iam_aad_l` | `azure:aad:device` | `api:azure:aad:device` |
| `azure_ad` | `azure:aad:signin` | `ms_aad_signins:tenant_id:{guid}` | `res_non_sec_iam_aad_l` | `azure:aad:signin` | `api:azure:aad:signin` |
| `azure_ad` | `azure:aad:user` | `ms_aad_user:tenant_id:{guid}` | `res_non_sec_iam_aad_l` | `azure:aad:user` | `api:azure:aad:user` |
| `brocade` | `syslog` | `udp:5020` | `ops_non_inf_stg_m` | `brocade:fabric:syslog` | `net:brocade:fabric:syslog` |
| `cim_modactions` | `modular_alerts:notable` | `/opt/splunk/var/log/splunk/notable_modalert.log` | `cim_modactions` | `modular_alerts:notable` | `splunk:modalert:notable` |
| `cim_modactions` | `modular_alerts:risk` | `/opt/splunk/var/log/splunk/risk_modalert.log` | `cim_modactions` | `modular_alerts:risk` | `splunk:modalert:risk` |
| `cisco` | `cisco:ios` | `udp:5514` | `ops_non_inf_ndl_m` | `cisco:ios` | `net:cisco:ios:syslog` |
| `cisco` | `cisco:ios:traceback` | `udp:5514` | `ops_non_inf_ndl_m` | `cisco:ios:traceback` | `net:cisco:ios:syslog` |
| `dlx_kpi` | `stash` | `dlx_kpi_global` | `dlx_kpi` | `stash` | `es:dlx:dlx_kpi_global` |
| `dlx_kpi` | `stash` | `dlx_kpi_individual` | `dlx_kpi` | `stash` | `es:dlx:dlx_kpi_individual` |
| `endpoint_summary` | `stash` | `Endpoint - Average Infection Length - Summary Gen` | `endpoint_summary` | `stash` | `es:summary:endpoint` |
| `ers` | `json` | `ers_diagnostics` | `ers` | `splunk:ers:diagnostics` | `es:ers:diagnostics` |
| `ers` | `stash` | `ers_breakdown` | `ers` | `stash` | `es:ers:ers_breakdown` |
| `ers` | `stash` | `ers_execution` | `ers` | `stash` | `es:ers:ers_execution` |
| `ers` | `stash` | `ers_history` | `ers` | `stash` | `es:ers:ers_history` |
| `f5` | `f5:bigip:ltm:ssl:error` | `udp:5015` | `ops_non_inf_ndl_m` | `f5:bigip:ltm:ssl:error` | `net:f5:bigip:syslog` |
| `f5` | `f5:bigip:syslog` | `udp:5015` | `ops_non_inf_ndl_m` | `f5:bigip:syslog` | `net:f5:bigip:syslog` |
| `forescout` | `fsctcenter_avp` | `udp:5055` | `res_non_sec_nac_m` | `forescout:counteract:avp` | `net:forescout:counteract:syslog` |
| `forescout` | `fsctcenter_json` | `CounterACT` | `res_non_sec_nac_m` | `forescout:counteract:json` | `api:forescout:counteract:events` |
| `gia_summary` | `stash` | `Access - Geographically Improbable Access - Summary Gen` | `gia_summary` | `stash` | `es:summary:gia` |
| `infoblox` | `infoblox:dhcp` | `udp:5053` | `ops_non_inf_dns_m` | `infoblox:dhcp` | `net:infoblox:dhcp` |
| `infoblox` | `infoblox:dns` | `udp:5053` | `ops_non_inf_dns_m` | `infoblox:dns` | `net:infoblox:dns` |
| `infoblox` | `infoblox:port` | `udp:5053` | `ops_non_inf_dns_m` | `infoblox:port` | `net:infoblox:port` |
| `msad` | `ActiveDirectory` | `ActiveDirectory` | `res_non_sec_iam_ad_m` | `microsoft:ad:directory` | `api:msad:directory` |
| `netapp` | `syslog` | `tcp:5008` | `ops_non_inf_stg_m` | `netapp:ontap:syslog` | `net:netapp:ontap:syslog` |
| `netapp` | `syslog` | `udp:5008` | `ops_non_inf_stg_m` | `netapp:ontap:syslog` | `net:netapp:ontap:syslog` |
| `notable` | `stash` | `ESCU - HTTP Malware User Agent - Rule` | `notable` | `stash` | `es:notable:escu_http_malware_user_agent_rule` |
| `notable` | `stash` | `ESCU - O365 External Guest User Invited - Rule` | `notable` | `stash` | `es:notable:escu_o365_external_guest_user_invited_rule` |
| `notable` | `stash` | `Threat - TSGT-ESCU - System User Discovery With Whoami - Rule - Rule` | `notable` | `stash` | `es:notable:threat_tsgt-escu_system_user_discovery_with_whoami_rule_rule` |
| `nps_server` | `WinHostMon` | `process` | `ops_non_inf_whm_s` | `microsoft:windows:hostmon` | `win:hostmon:process` |
| `nps_server` | `WinHostMon` | `processor` | `ops_non_inf_whm_s` | `microsoft:windows:hostmon` | `win:hostmon:processor` |
| `nps_server` | `WinHostMon` | `roles` | `ops_non_inf_whm_s` | `microsoft:windows:hostmon` | `win:hostmon:roles` |
| `nps_server` | `WinHostMon` | `service` | `ops_non_inf_whm_s` | `microsoft:windows:hostmon` | `win:hostmon:service` |
| `nps_server` | `XmlWinEventLog` | `XmlWinEventLog:Application` | `res_non_sec_iam_nps_l` | `microsoft:windows:eventlog:xml` | `win:nps:eventlog:application` |
| `nps_server` | `XmlWinEventLog` | `XmlWinEventLog:Security` | `res_non_sec_iam_nps_l` | `microsoft:windows:eventlog:xml` | `win:nps:eventlog:security` |
| `nps_server` | `XmlWinEventLog` | `XmlWinEventLog:System` | `res_non_sec_iam_nps_l` | `microsoft:windows:eventlog:xml` | `win:nps:eventlog:system` |
| `o365` | `ms365:defender:incident` | `microsoft_365_defender_endpoint_incidents:{guid}` | `res_non_sec_edr_l` | `ms365:defender:incident` | `api:ms365:defender:incident` |
| `o365` | `ms365:defender:incident:alerts` | `microsoft_365_defender_endpoint_incidents:{guid}` | `res_non_sec_edr_l` | `ms365:defender:incident:alerts` | `api:ms365:defender:incident` |
| `o365` | `o365:management:activity` | `https://{host}/api/v1.0/{guid}/activity/feed/audit/{timestamp}${timestamp}$audit_azureactivedirectory$Audit_AzureActiveDirectory$na0047` | `ent_non_app_col_o365_m` | `o365:management:activity` | `api:o365:management:activity` |
| `o365` | `o365:management:activity` | `https://{host}/api/v1.0/{guid}/activity/feed/audit/{timestamp}${timestamp}$audit_exchange$Audit_Exchange$na0047` | `ent_non_app_col_o365_m` | `o365:management:activity` | `api:o365:management:activity` |
| `o365` | `o365:management:activity` | `https://{host}/api/v1.0/{guid}/activity/feed/audit/{timestamp}${timestamp}$audit_sharepoint$Audit_SharePoint$na0047` | `ent_non_app_col_o365_m` | `o365:management:activity` | `api:o365:management:activity` |
| `o365` | `o365:service:healthIssue` | `ServiceAnnouncement.Issues` | `ent_non_app_col_o365_m` | `o365:service:healthissue` | `api:o365:service:healthissue` |
| `o365` | `o365:service:updateMessage` | `ServiceAnnouncement.Messages` | `ent_non_app_col_o365_m` | `o365:service:updatemessage` | `api:o365:service:updatemessage` |
| `okta` | `OktaIM2:log` | `http:Okta` | `res_non_sec_iam_okt_l` | `okta:identity:log` | `api:okta:identity:log` |
| `oracle` | `App` | `oci_logging://OCI_Audit` | `res_non_sec_iam_oci_l` | `oracle:idcs:audit` | `api:oracle:idcs:audit` |
| `oracle` | `App` | `oci_logging://OCI_Audit
svc_oci_network_diagram` | `res_non_sec_iam_oci_l` | `oracle:idcs:audit` | `api:oracle:idcs:audit` |
| `oracle` | `App` | `oci_logging://OCI_Audit
user_12d{digits}@example.invalid` | `res_non_sec_iam_oci_l` | `oracle:idcs:audit` | `api:oracle:idcs:audit` |
| `oracle` | `App` | `oci_logging://OCI_Audit
user_1e{digits}@example.invalid` | `res_non_sec_iam_oci_l` | `oracle:idcs:audit` | `api:oracle:idcs:audit` |
| `oracle` | `App` | `oci_logging://OCI_Audit
user_2e8f6228@example.invalid` | `res_non_sec_iam_oci_l` | `oracle:idcs:audit` | `api:oracle:idcs:audit` |
| `oracle` | `App` | `oci_logging://OCI_Audit
user_3f7fdd16@example.invalid` | `res_non_sec_iam_oci_l` | `oracle:idcs:audit` | `api:oracle:idcs:audit` |
| `oracle` | `App` | `oci_logging://OCI_Audit
user_48eccef0@example.invalid` | `res_non_sec_iam_oci_l` | `oracle:idcs:audit` | `api:oracle:idcs:audit` |
| `oracle` | `App` | `oci_logging://OCI_Audit
user_597f1d26@example.invalid` | `res_non_sec_iam_oci_l` | `oracle:idcs:audit` | `api:oracle:idcs:audit` |
| `oracle` | `App` | `oci_logging://OCI_Audit
user_c{digits}@example.invalid` | `res_non_sec_iam_oci_l` | `oracle:idcs:audit` | `api:oracle:idcs:audit` |
| `oracle` | `App` | `oci_logging://OCI_Audit
user_e19cc051@example.invalid` | `res_non_sec_iam_oci_l` | `oracle:idcs:audit` | `api:oracle:idcs:audit` |
| `oracle` | `App` | `oci_logging://OCI_Audit
user_f20b5ddf@example.invalid` | `res_non_sec_iam_oci_l` | `oracle:idcs:audit` | `api:oracle:idcs:audit` |
| `oracle` | `App` | `oci_logging://OCI_Audit
{hash}` | `res_non_sec_iam_oci_l` | `oracle:idcs:audit` | `api:oracle:idcs:audit` |
| `oracle` | `PHONE_CALL` | `oci_logging://OCI_Audit
{hash}` | `res_non_sec_iam_oci_l` | `oracle:idcs:mfa` | `api:oracle:idcs:mfa` |
| `oracle` | `SMS` | `oci_logging://OCI_Audit
{hash}` | `res_non_sec_iam_oci_l` | `oracle:idcs:mfa` | `api:oracle:idcs:mfa` |
| `oracle` | `TOTP` | `oci_logging://OCI_Audit
{hash}` | `res_non_sec_iam_oci_l` | `oracle:idcs:mfa` | `api:oracle:idcs:mfa` |
| `oracle` | `User` | `oci_logging://OCI_Audit` | `res_non_sec_iam_oci_l` | `oracle:idcs:audit` | `api:oracle:idcs:audit` |
| `oracle` | `User` | `oci_logging://OCI_Audit
{hash}` | `res_non_sec_iam_oci_l` | `oracle:idcs:audit` | `api:oracle:idcs:audit` |
| `oracle` | `com.or` | `oci_logging://OCI_Audit` | `ops_non_inf_bad_s` | `oracle:oci:malformed` | `api:oracle:oci:audit` |
| `oracle` | `com.orac` | `oci_logging://OCI_Audit` | `ops_non_inf_bad_s` | `oracle:oci:malformed` | `api:oracle:oci:audit` |
| `oracle` | `com.oracle` | `oci_logging://OCI_Audit` | `ops_non_inf_bad_s` | `oracle:oci:malformed` | `api:oracle:oci:audit` |
| `oracle` | `com.oraclecl` | `oci_logging://OCI_Audit` | `ops_non_inf_bad_s` | `oracle:oci:malformed` | `api:oracle:oci:audit` |
| `oracle` | `com.oraclecloud.Announcements-live.ListAnnouncements` | `oci_logging://OCI_Audit` | `ops_non_inf_ocl_m` | `oracle:oci:audit` | `api:oracle:oci:audit` |
| `oracle` | `com.oraclecloud.BlockVolumes.CreateBootVolumeBackup.begin` | `oci_logging://OCI_Audit
Auto-backup for pocvldebsapps via policy: gold on 2026-08-18 07:00:00` | `ops_non_inf_ocl_m` | `oracle:oci:audit` | `api:oracle:oci:audit` |
| `oracle` | `com.oraclecloud.BlockVolumes.CreateBootVolumeBackup.end` | `oci_logging://OCI_Audit
Auto-backup for pocvldebsapps via policy: gold on 2026-08-18 07:00:00` | `ops_non_inf_ocl_m` | `oracle:oci:audit` | `api:oracle:oci:audit` |
| `oracle` | `com.oraclecloud.BlockVolumes.CreateVolumeBackup.begin` | `oci_logging://OCI_Audit
Auto-backup for pocvldebsapps-blk-01 via policy: gold on 2026-08-18 07:00:00` | `ops_non_inf_ocl_m` | `oracle:oci:audit` | `api:oracle:oci:audit` |
| `oracle` | `com.oraclecloud.BlockVolumes.CreateVolumeBackup.end` | `oci_logging://OCI_Audit
Auto-backup for pocvldebsapps-blk-01 via policy: gold on 2026-08-18 07:00:00` | `ops_non_inf_ocl_m` | `oracle:oci:audit` | `api:oracle:oci:audit` |
| `oracle` | `com.oraclecloud.BlockVolumes.DeleteBootVolumeBackup.end` | `oci_logging://OCI_Audit
Auto-backup for pocvldebsapps via policy: gold on 2026-08-11 07:00:00` | `ops_non_inf_ocl_m` | `oracle:oci:audit` | `api:oracle:oci:audit` |
| `oracle` | `com.oraclecloud.BlockVolumes.DeleteVolumeBackup.end` | `oci_logging://OCI_Audit
Auto-backup for pocvldebsapps-blk-01 via policy: gold on 2026-08-11 07:00:00` | `ops_non_inf_ocl_m` | `oracle:oci:audit` | `api:oracle:oci:audit` |
| `oracle` | `com.oraclecloud.BlockVolumes.ListVolumes` | `oci_logging://OCI_Audit` | `ops_non_inf_ocl_m` | `oracle:oci:audit` | `api:oracle:oci:audit` |
| `oracle` | `com.oraclecloud.Compartments.GetCompartment` | `oci_logging://OCI_Audit` | `ops_non_inf_ocl_m` | `oracle:oci:audit` | `api:oracle:oci:audit` |
| `oracle` | `com.oraclecloud.Compartments.GetCompartment` | `oci_logging://OCI_Audit
DEV` | `ops_non_inf_ocl_m` | `oracle:oci:audit` | `api:oracle:oci:audit` |
| `oracle` | `com.oraclecloud.Compartments.GetCompartment` | `oci_logging://OCI_Audit
PROD` | `ops_non_inf_ocl_m` | `oracle:oci:audit` | `api:oracle:oci:audit` |
| `oracle` | `com.oraclecloud.Compartments.GetCompartment` | `oci_logging://OCI_Audit
tsgt` | `ops_non_inf_ocl_m` | `oracle:oci:audit` | `api:oracle:oci:audit` |
| `oracle` | `com.oraclecloud.Compartments.GetTenancy` | `oci_logging://OCI_Audit
tsgt` | `ops_non_inf_ocl_m` | `oracle:oci:audit` | `api:oracle:oci:audit` |
| `oracle` | `com.oraclecloud.Compartments.ListAvailabilityDomains` | `oci_logging://OCI_Audit` | `ops_non_inf_ocl_m` | `oracle:oci:audit` | `api:oracle:oci:audit` |
| `oracle` | `com.oraclecloud.Compartments.ListCompartments` | `oci_logging://OCI_Audit` | `ops_non_inf_ocl_m` | `oracle:oci:audit` | `api:oracle:oci:audit` |
| `oracle` | `com.oraclecloud.Compartments.ListRegionSubscriptions` | `oci_logging://OCI_Audit` | `ops_non_inf_ocl_m` | `oracle:oci:audit` | `api:oracle:oci:audit` |
| `oracle` | `com.oraclecloud.Compartments.ListTenancyCompartmentTree` | `oci_logging://OCI_Audit` | `ops_non_inf_ocl_m` | `oracle:oci:audit` | `api:oracle:oci:audit` |
| `oracle` | `com.oraclecloud.DatabaseService.AutomaticBackupDatabase.begin` | `oci_logging://OCI_Audit
Automatic Backup` | `ops_non_inf_ocl_m` | `oracle:oci:audit` | `api:oracle:oci:audit` |
| `oracle` | `com.oraclecloud.DatabaseService.AutomaticBackupDatabase.end` | `oci_logging://OCI_Audit
Automatic Backup` | `ops_non_inf_ocl_m` | `oracle:oci:audit` | `api:oracle:oci:audit` |
| `oracle` | `com.oraclecloud.DatabaseService.GetAutonomousDatabaseRegionWallet` | `oci_logging://OCI_Audit` | `ops_non_inf_ocl_m` | `oracle:oci:audit` | `api:oracle:oci:audit` |
| `oracle` | `com.oraclecloud.DatabaseService.ListAutonomousDatabases` | `oci_logging://OCI_Audit` | `ops_non_inf_ocl_m` | `oracle:oci:audit` | `api:oracle:oci:audit` |
| `oracle` | `com.oraclecloud.DatabaseService.ListDataGuardAssociations` | `oci_logging://OCI_Audit` | `ops_non_inf_ocl_m` | `oracle:oci:audit` | `api:oracle:oci:audit` |
| `oracle` | `com.oraclecloud.DatabaseService.ListDatabases` | `oci_logging://OCI_Audit` | `ops_non_inf_ocl_m` | `oracle:oci:audit` | `api:oracle:oci:audit` |
| `oracle` | `com.oraclecloud.DatabaseService.ListDbHomePatches` | `oci_logging://OCI_Audit` | `ops_non_inf_ocl_m` | `oracle:oci:audit` | `api:oracle:oci:audit` |
| `oracle` | `com.oraclecloud.DatabaseService.ListDbHomes` | `oci_logging://OCI_Audit` | `ops_non_inf_ocl_m` | `oracle:oci:audit` | `api:oracle:oci:audit` |
| `oracle` | `com.oraclecloud.DatabaseService.ListDbNodes` | `oci_logging://OCI_Audit` | `ops_non_inf_ocl_m` | `oracle:oci:audit` | `api:oracle:oci:audit` |
| `oracle` | `com.oraclecloud.DatabaseService.ListDbSystems` | `oci_logging://OCI_Audit` | `ops_non_inf_ocl_m` | `oracle:oci:audit` | `api:oracle:oci:audit` |
| `oracle` | `com.oraclecloud.FusionApps.GetFusionEnvironment` | `oci_logging://OCI_Audit
exbd-dev1` | `ops_non_inf_ocl_m` | `oracle:oci:audit` | `api:oracle:oci:audit` |
| `oracle` | `com.oraclecloud.FusionApps.GetFusionEnvironmentFamily` | `oci_logging://OCI_Audit
exbd-FAMILY` | `ops_non_inf_ocl_m` | `oracle:oci:audit` | `api:oracle:oci:audit` |
| `oracle` | `com.oraclecloud.FusionApps.GetFusionEnvironmentFamilySubscriptionDetail` | `oci_logging://OCI_Audit` | `ops_non_inf_ocl_m` | `oracle:oci:audit` | `api:oracle:oci:audit` |
| `oracle` | `com.oraclecloud.FusionApps.GetFusionEnvironmentStatus` | `oci_logging://OCI_Audit` | `ops_non_inf_ocl_m` | `oracle:oci:audit` | `api:oracle:oci:audit` |
| `oracle` | `com.oraclecloud.FusionApps.ListFusionEnvironmentFamilies` | `oci_logging://OCI_Audit` | `ops_non_inf_ocl_m` | `oracle:oci:audit` | `api:oracle:oci:audit` |
| `oracle` | `com.oraclecloud.FusionApps.ListFusionEnvironments` | `oci_logging://OCI_Audit` | `ops_non_inf_ocl_m` | `oracle:oci:audit` | `api:oracle:oci:audit` |
| `oracle` | `com.oraclecloud.FusionApps.ListRefreshActivities` | `oci_logging://OCI_Audit` | `ops_non_inf_ocl_m` | `oracle:oci:audit` | `api:oracle:oci:audit` |
| `oracle` | `com.oraclecloud.FusionApps.ListScheduledActivities` | `oci_logging://OCI_Audit` | `ops_non_inf_ocl_m` | `oracle:oci:audit` | `api:oracle:oci:audit` |
| `oracle` | `com.oraclecloud.FusionApps.ListVanityDomains` | `oci_logging://OCI_Audit` | `ops_non_inf_ocl_m` | `oracle:oci:audit` | `api:oracle:oci:audit` |
| `oracle` | `com.oraclecloud.FusionAppsInternal.UpdateRollbackPoint` | `oci_logging://OCI_Audit` | `ops_non_inf_ocl_m` | `oracle:oci:audit` | `api:oracle:oci:audit` |
| `oracle` | `com.oraclecloud.IdentitySignOn.Cr` | `oci_logging://OCI_Audit` | `ops_non_inf_ocl_m` | `oracle:oci:audit` | `api:oracle:oci:audit` |
| `oracle` | `com.oraclecloud.LoggingAnalytics.ListCores` | `oci_logging://OCI_Audit` | `ops_non_inf_ocl_m` | `oracle:oci:audit` | `api:oracle:oci:audit` |
| `oracle` | `com.oraclecloud.LoggingAnalytics.UploadOCSFile` | `oci_logging://OCI_Audit` | `ops_non_inf_ocl_m` | `oracle:oci:audit` | `api:oracle:oci:audit` |
| `oracle` | `com.oraclecloud.Mysqlaas.ListDbSystems` | `oci_logging://OCI_Audit` | `ops_non_inf_ocl_m` | `oracle:oci:audit` | `api:oracle:oci:audit` |
| `oracle` | `com.oraclecloud.OraLB-API.ListLoadBalancers` | `oci_logging://OCI_Audit` | `ops_non_inf_ocl_m` | `oracle:oci:audit` | `api:oracle:oci:audit` |
| `oracle` | `com.oraclecloud.PublicApiTelemetry.SummarizeMetricsData` | `oci_logging://OCI_Audit` | `ops_non_inf_ocl_m` | `oracle:oci:audit` | `api:oracle:oci:audit` |
| `oracle` | `com.oraclecloud.VisualBuilder.GetResourcePrincipalDetails` | `oci_logging://OCI_Audit` | `ops_non_inf_ocl_m` | `oracle:oci:audit` | `api:oracle:oci:audit` |
| `oracle` | `com.oraclecloud.analytics.GetAnalyticsInstance` | `oci_logging://OCI_Audit
oaxTSGTFAWProd` | `ops_non_inf_ocl_m` | `oracle:oci:audit` | `api:oracle:oci:audit` |
| `oracle` | `com.oraclecloud.analytics.GetAnalyticsInstance` | `oci_logging://OCI_Audit
oaxTSGTFDIDev2` | `ops_non_inf_ocl_m` | `oracle:oci:audit` | `api:oracle:oci:audit` |
| `oracle` | `com.oraclecloud.apigateway.listgateways` | `oci_logging://OCI_Audit` | `ops_non_inf_ocl_m` | `oracle:oci:audit` | `api:oracle:oci:audit` |
| `oracle` | `com.oraclecloud.bastion.GetBastion` | `oci_logging://OCI_Audit
ATPDEVDBBASTION` | `ops_non_inf_ocl_m` | `oracle:oci:audit` | `api:oracle:oci:audit` |
| `oracle` | `com.oraclecloud.bastion.GetBastion` | `oci_logging://OCI_Audit
Bastion{digits}` | `ops_non_inf_ocl_m` | `oracle:oci:audit` | `api:oracle:oci:audit` |
| `oracle` | `com.oraclecloud.bastion.GetBastion` | `oci_logging://OCI_Audit
CSSNONPRODBASTION` | `ops_non_inf_ocl_m` | `oracle:oci:audit` | `api:oracle:oci:audit` |
| `oracle` | `com.oraclecloud.bastion.GetBastion` | `oci_logging://OCI_Audit
TSGTLZDEVBASTION1` | `ops_non_inf_ocl_m` | `oracle:oci:audit` | `api:oracle:oci:audit` |
| `oracle` | `com.oraclecloud.bastion.ListBastions` | `oci_logging://OCI_Audit` | `ops_non_inf_ocl_m` | `oracle:oci:audit` | `api:oracle:oci:audit` |
| `oracle` | `com.oraclecloud.computeApi.ListInstances` | `oci_logging://OCI_Audit` | `ops_non_inf_ocl_m` | `oracle:oci:audit` | `api:oracle:oci:audit` |
| `oracle` | `com.oraclecloud.computeApi.ListVnicAttachments` | `oci_logging://OCI_Audit` | `ops_non_inf_ocl_m` | `oracle:oci:audit` | `api:oracle:oci:audit` |
| `oracle` | `com.oraclecloud.computeApi.ListVolumeAttachments` | `oci_logging://OCI_Audit` | `ops_non_inf_ocl_m` | `oracle:oci:audit` | `api:oracle:oci:audit` |
| `oracle` | `com.oraclecloud.databaseservice.ListAutonomousDatabases` | `oci_logging://OCI_Audit` | `ops_non_inf_ocl_m` | `oracle:oci:audit` | `api:oracle:oci:audit` |
| `oracle` | `com.oraclecloud.databaseservice.ListDatabases` | `oci_logging://OCI_Audit` | `ops_non_inf_ocl_m` | `oracle:oci:audit` | `api:oracle:oci:audit` |
| `oracle` | `com.oraclecloud.databaseservice.ListDbHomes` | `oci_logging://OCI_Audit` | `ops_non_inf_ocl_m` | `oracle:oci:audit` | `api:oracle:oci:audit` |
| `oracle` | `com.oraclecloud.databaseservice.ListDbNodes` | `oci_logging://OCI_Audit` | `ops_non_inf_ocl_m` | `oracle:oci:audit` | `api:oracle:oci:audit` |
| `oracle` | `com.oraclecloud.databaseservice.ListDbSystems` | `oci_logging://OCI_Audit` | `ops_non_inf_ocl_m` | `oracle:oci:audit` | `api:oracle:oci:audit` |
| `oracle` | `com.oraclecloud.identityControlPlane.EmailNotificationDeliveryStatus` | `oci_logging://OCI_Audit` | `ops_non_inf_ocl_m` | `oracle:oci:audit` | `api:oracle:oci:audit` |
| `oracle` | `com.oraclecloud.identityControlPlane.GetDenyPolicyFeatureStatus` | `oci_logging://OCI_Audit` | `ops_non_inf_ocl_m` | `oracle:oci:audit` | `api:oracle:oci:audit` |
| `oracle` | `com.oraclecloud.identityControlPlane.GetDomain` | `oci_logging://OCI_Audit
oracleidentitycloudservice` | `ops_non_inf_ocl_m` | `oracle:oci:audit` | `api:oracle:oci:audit` |
| `oracle` | `com.oraclecloud.identityControlPlane.GetPolicy` | `oci_logging://OCI_Audit
OKIT_Network_Diagram_Read_Tenant` | `ops_non_inf_ocl_m` | `oracle:oci:audit` | `api:oracle:oci:audit` |
| `oracle` | `com.oraclecloud.identityControlPlane.GetPolicy` | `oci_logging://OCI_Audit
TSGTLZ-it-hosted-team-policy` | `ops_non_inf_ocl_m` | `oracle:oci:audit` | `api:oracle:oci:audit` |
| `oracle` | `com.oraclecloud.identityControlPlane.GetPolicy` | `oci_logging://OCI_Audit
TSGTLZ-security-admin-policy` | `ops_non_inf_ocl_m` | `oracle:oci:audit` | `api:oracle:oci:audit` |
| `oracle` | `com.oraclecloud.identityControlPlane.ListAllowedDomainLicenseTypes` | `oci_logging://OCI_Audit` | `ops_non_inf_ocl_m` | `oracle:oci:audit` | `api:oracle:oci:audit` |
| `oracle` | `com.oraclecloud.identityControlPlane.ListDomains` | `oci_logging://OCI_Audit
Domain` | `ops_non_inf_ocl_m` | `oracle:oci:audit` | `api:oracle:oci:audit` |
| `oracle` | `com.oraclecloud.identityControlPlane.ListDynamicGroups` | `oci_logging://OCI_Audit
DynamicGroup` | `ops_non_inf_ocl_m` | `oracle:oci:audit` | `api:oracle:oci:audit` |
| `oracle` | `com.oraclecloud.identityControlPlane.ListGroups` | `oci_logging://OCI_Audit
Group` | `ops_non_inf_ocl_m` | `oracle:oci:audit` | `api:oracle:oci:audit` |
| `oracle` | `com.oraclecloud.identityControlPlane.ListPolicySimulations` | `oci_logging://OCI_Audit` | `ops_non_inf_ocl_m` | `oracle:oci:audit` | `api:oracle:oci:audit` |
| `oracle` | `com.oraclecloud.identityControlPlane.ListUsers` | `oci_logging://OCI_Audit
User` | `ops_non_inf_ocl_m` | `oracle:oci:audit` | `api:oracle:oci:audit` |
| `oracle` | `com.oraclecloud.limits.GetResourceAvailability` | `oci_logging://OCI_Audit` | `ops_non_inf_ocl_m` | `oracle:oci:audit` | `api:oracle:oci:audit` |
| `oracle` | `com.oraclecloud.limits.ListLimitValues` | `oci_logging://OCI_Audit` | `ops_non_inf_ocl_m` | `oracle:oci:audit` | `api:oracle:oci:audit` |
| `oracle` | `com.oraclecloud.limits.ListQuotas` | `oci_logging://OCI_Audit` | `ops_non_inf_ocl_m` | `oracle:oci:audit` | `api:oracle:oci:audit` |
| `oracle` | `com.oraclecloud.logging.GetGeneratedUnifiedAgentConfiguration` | `oci_logging://OCI_Audit` | `ops_non_inf_ocl_m` | `oracle:oci:audit` | `api:oracle:oci:audit` |
| `oracle` | `com.oraclecloud.logging.ListLogGroups` | `oci_logging://OCI_Audit` | `ops_non_inf_ocl_m` | `oracle:oci:audit` | `api:oracle:oci:audit` |
| `oracle` | `com.oraclecloud.logging.ListLogs` | `oci_logging://OCI_Audit` | `ops_non_inf_ocl_m` | `oracle:oci:audit` | `api:oracle:oci:audit` |
| `oracle` | `com.oraclecloud.natgateway.ListDrgs` | `oci_logging://OCI_Audit` | `ops_non_inf_ocl_m` | `oracle:oci:audit` | `api:oracle:oci:audit` |
| `oracle` | `com.oraclecloud.natgateway.ListNatGateways` | `oci_logging://OCI_Audit` | `ops_non_inf_ocl_m` | `oracle:oci:audit` | `api:oracle:oci:audit` |
| `oracle` | `com.oraclecloud.notification.GetTopic` | `oci_logging://OCI_Audit
TSGTLZ-MFA-topic` | `ops_non_inf_ocl_m` | `oracle:oci:audit` | `api:oracle:oci:audit` |
| `oracle` | `com.oraclecloud.notification.GetTopic` | `oci_logging://OCI_Audit
TSGTLZ-cloudguard-topic` | `ops_non_inf_ocl_m` | `oracle:oci:audit` | `api:oracle:oci:audit` |
| `oracle` | `com.oraclecloud.notification.GetTopic` | `oci_logging://OCI_Audit
TSGTLZ-security-topic` | `ops_non_inf_ocl_m` | `oracle:oci:audit` | `api:oracle:oci:audit` |
| `oracle` | `com.oraclecloud.objectstorage.getnamespace` | `oci_logging://OCI_Audit
/n` | `ops_non_inf_ocl_m` | `oracle:oci:audit` | `api:oracle:oci:audit` |
| `oracle` | `com.oraclecloud.personalization-service-prod.ListPreferences` | `oci_logging://OCI_Audit` | `ops_non_inf_ocl_m` | `oracle:oci:audit` | `api:oracle:oci:audit` |
| `oracle` | `com.oraclecloud.postgresql.ListDbSystems` | `oci_logging://OCI_Audit` | `ops_non_inf_ocl_m` | `oracle:oci:audit` | `api:oracle:oci:audit` |
| `oracle` | `com.oraclecloud.service-manager-proxy.ListServiceEnvironments` | `oci_logging://OCI_Audit` | `ops_non_inf_ocl_m` | `oracle:oci:audit` | `api:oracle:oci:audit` |
| `oracle` | `com.oraclecloud.servicegateway.GetPrivateEndpoint` | `oci_logging://OCI_Audit
PE_us-phoenix-1_{guid}` | `ops_non_inf_ocl_m` | `oracle:oci:audit` | `api:oracle:oci:audit` |
| `oracle` | `com.oraclecloud.servicegateway.GetPrivateEndpoint` | `oci_logging://OCI_Audit
TSGT_Forward` | `ops_non_inf_ocl_m` | `oracle:oci:audit` | `api:oracle:oci:audit` |
| `oracle` | `com.oraclecloud.servicegateway.GetPrivateEndpoint` | `oci_logging://OCI_Audit
ocid1.bastion.oc1.phx.amaaaaaaylygzbqa24lacbzs6ua42wkestcc6ziyk2wa7xaedifexfpfw6yq` | `ops_non_inf_ocl_m` | `oracle:oci:audit` | `api:oracle:oci:audit` |
| `oracle` | `com.oraclecloud.servicegateway.GetPrivateEndpoint` | `oci_logging://OCI_Audit
ocid1.bastion.oc1.phx.amaaaaaaylygzbqamkjtsj3nqoidi7dz6m3bln44nk3y2o4pgms33dww4h4a` | `ops_non_inf_ocl_m` | `oracle:oci:audit` | `api:oracle:oci:audit` |
| `oracle` | `com.oraclecloud.servicegateway.GetPrivateEndpoint` | `oci_logging://OCI_Audit
ocid1.bastion.oc1.phx.amaaaaaaylygzbqaragg46rq55n772shcjqs4zqdka3h4acvd4bn3vtirkha` | `ops_non_inf_ocl_m` | `oracle:oci:audit` | `api:oracle:oci:audit` |
| `oracle` | `com.oraclecloud.servicegateway.GetPrivateEndpoint` | `oci_logging://OCI_Audit
ocid1.bastion.oc1.phx.amaaaaaaylygzbqarxxagnejvxhcalxzqqdkx56ipqllzerknvtnecy2mbia` | `ops_non_inf_ocl_m` | `oracle:oci:audit` | `api:oracle:oci:audit` |
| `oracle` | `com.oraclecloud.servicegateway.ListEndpointServices` | `oci_logging://OCI_Audit` | `ops_non_inf_ocl_m` | `oracle:oci:audit` | `api:oracle:oci:audit` |
| `oracle` | `com.oraclecloud.servicegateway.ListPrivateEndpoints` | `oci_logging://OCI_Audit` | `ops_non_inf_ocl_m` | `oracle:oci:audit` | `api:oracle:oci:audit` |
| `oracle` | `com.oraclecloud.servicegateway.ListServiceGateways` | `oci_logging://OCI_Audit` | `ops_non_inf_ocl_m` | `oracle:oci:audit` | `api:oracle:oci:audit` |
| `oracle` | `com.oraclecloud.taggingControlPlane.ListCostTrackingTags` | `oci_logging://OCI_Audit` | `ops_non_inf_ocl_m` | `oracle:oci:audit` | `api:oracle:oci:audit` |
| `oracle` | `com.oraclecloud.taggingControlPlane.ListTagDefaults` | `oci_logging://OCI_Audit` | `ops_non_inf_ocl_m` | `oracle:oci:audit` | `api:oracle:oci:audit` |
| `oracle` | `com.oraclecloud.taggingControlPlane.ListTagDefinitions` | `oci_logging://OCI_Audit` | `ops_non_inf_ocl_m` | `oracle:oci:audit` | `api:oracle:oci:audit` |
| `oracle` | `com.oraclecloud.taggingControlPlane.ListTagNamespaces` | `oci_logging://OCI_Audit
TagNamespace` | `ops_non_inf_ocl_m` | `oracle:oci:audit` | `api:oracle:oci:audit` |
| `oracle` | `com.oraclecloud.tenant-manager-api-cp-external.GetAssignedSubscription` | `oci_logging://OCI_Audit` | `ops_non_inf_ocl_m` | `oracle:oci:audit` | `api:oracle:oci:audit` |
| `oracle` | `com.oraclecloud.tenant-manager-api-cp-external.ListAssignedSubscriptions` | `oci_logging://OCI_Audit` | `ops_non_inf_ocl_m` | `oracle:oci:audit` | `api:oracle:oci:audit` |
| `oracle` | `com.oraclecloud.tenant-manager-api-cp-external.ListLinks` | `oci_logging://OCI_Audit` | `ops_non_inf_ocl_m` | `oracle:oci:audit` | `api:oracle:oci:audit` |
| `oracle` | `com.oraclecloud.tenant-manager-api-cp-external.ListOrganizations` | `oci_logging://OCI_Audit` | `ops_non_inf_ocl_m` | `oracle:oci:audit` | `api:oracle:oci:audit` |
| `oracle` | `com.oraclecloud.tenant-manager-api-cp-external.ListSubscriptions` | `oci_logging://OCI_Audit` | `ops_non_inf_ocl_m` | `oracle:oci:audit` | `api:oracle:oci:audit` |
| `oracle` | `com.oraclecloud.usage.ListOrganizationSubscriptions` | `oci_logging://OCI_Audit` | `ops_non_inf_ocl_m` | `oracle:oci:audit` | `api:oracle:oci:audit` |
| `oracle` | `com.oraclecloud.usage.ListSubscriptions` | `oci_logging://OCI_Audit` | `ops_non_inf_ocl_m` | `oracle:oci:audit` | `api:oracle:oci:audit` |
| `oracle` | `com.oraclecloud.virtualNetwork.GetSubnet` | `oci_logging://OCI_Audit` | `ops_non_inf_ocl_m` | `oracle:oci:audit` | `api:oracle:oci:audit` |
| `oracle` | `com.oraclecloud.virtualNetwork.GetSubnet` | `oci_logging://OCI_Audit
TSGTLZVCN-app-subnet_192.168.225.0_24` | `ops_non_inf_ocl_m` | `oracle:oci:audit` | `api:oracle:oci:audit` |
| `oracle` | `com.oraclecloud.virtualNetwork.GetSubnet` | `oci_logging://OCI_Audit
TSGTLZVCN-db-subnet_192.168.226.0_24` | `ops_non_inf_ocl_m` | `oracle:oci:audit` | `api:oracle:oci:audit` |
| `oracle` | `com.oraclecloud.virtualNetwork.GetVcn` | `oci_logging://OCI_Audit` | `ops_non_inf_ocl_m` | `oracle:oci:audit` | `api:oracle:oci:audit` |
| `oracle` | `com.oraclecloud.virtualNetwork.GetVnic` | `oci_logging://OCI_Audit` | `ops_non_inf_ocl_m` | `oracle:oci:audit` | `api:oracle:oci:audit` |
| `oracle` | `com.oraclecloud.virtualNetwork.GetVnic` | `oci_logging://OCI_Audit
Broadpin_Con_JH_01` | `ops_non_inf_ocl_m` | `oracle:oci:audit` | `api:oracle:oci:audit` |
| `oracle` | `com.oraclecloud.virtualNetwork.GetVnic` | `oci_logging://OCI_Audit
Broadpin_Con_JH_02` | `ops_non_inf_ocl_m` | `oracle:oci:audit` | `api:oracle:oci:audit` |
| `oracle` | `com.oraclecloud.virtualNetwork.GetVnic` | `oci_logging://OCI_Audit
CSSNONPRODCONAGENT-1` | `ops_non_inf_ocl_m` | `oracle:oci:audit` | `api:oracle:oci:audit` |
| `oracle` | `com.oraclecloud.virtualNetwork.GetVnic` | `oci_logging://OCI_Audit
Contractor_ProjectPartners_Team_JH_01` | `ops_non_inf_ocl_m` | `oracle:oci:audit` | `api:oracle:oci:audit` |
| `oracle` | `com.oraclecloud.virtualNetwork.GetVnic` | `oci_logging://OCI_Audit
Contractor_ProjectPartners_Team_JH_02` | `ops_non_inf_ocl_m` | `oracle:oci:audit` | `api:oracle:oci:audit` |
| `oracle` | `com.oraclecloud.virtualNetwork.GetVnic` | `oci_logging://OCI_Audit
Contractor_ProjectPartners_Team_JH_03` | `ops_non_inf_ocl_m` | `oracle:oci:audit` | `api:oracle:oci:audit` |
| `oracle` | `com.oraclecloud.virtualNetwork.GetVnic` | `oci_logging://OCI_Audit
DEV1CONAGENT-1` | `ops_non_inf_ocl_m` | `oracle:oci:audit` | `api:oracle:oci:audit` |
| `oracle` | `com.oraclecloud.virtualNetwork.GetVnic` | `oci_logging://OCI_Audit
DEV1CONAGENT-1-New` | `ops_non_inf_ocl_m` | `oracle:oci:audit` | `api:oracle:oci:audit` |
| `oracle` | `com.oraclecloud.virtualNetwork.GetVnic` | `oci_logging://OCI_Audit
DEV2CONAGENT-1` | `ops_non_inf_ocl_m` | `oracle:oci:audit` | `api:oracle:oci:audit` |
| `oracle` | `com.oraclecloud.virtualNetwork.GetVnic` | `oci_logging://OCI_Audit
DEV2CONAGENT-1-New` | `ops_non_inf_ocl_m` | `oracle:oci:audit` | `api:oracle:oci:audit` |
| `oracle` | `com.oraclecloud.virtualNetwork.GetVnic` | `oci_logging://OCI_Audit
DEV3CONAGENT-1` | `ops_non_inf_ocl_m` | `oracle:oci:audit` | `api:oracle:oci:audit` |
| `oracle` | `com.oraclecloud.virtualNetwork.GetVnic` | `oci_logging://OCI_Audit
DEV3CONAGENT-1-New` | `ops_non_inf_ocl_m` | `oracle:oci:audit` | `api:oracle:oci:audit` |
| `oracle` | `com.oraclecloud.virtualNetwork.GetVnic` | `oci_logging://OCI_Audit
IAM_Team_JumpHost` | `ops_non_inf_ocl_m` | `oracle:oci:audit` | `api:oracle:oci:audit` |
| `oracle` | `com.oraclecloud.virtualNetwork.GetVnic` | `oci_logging://OCI_Audit
PROD1CONAGENT-1` | `ops_non_inf_ocl_m` | `oracle:oci:audit` | `api:oracle:oci:audit` |
| `oracle` | `com.oraclecloud.virtualNetwork.GetVnic` | `oci_logging://OCI_Audit
PROD1CONAGENT-2` | `ops_non_inf_ocl_m` | `oracle:oci:audit` | `api:oracle:oci:audit` |
| `oracle` | `com.oraclecloud.virtualNetwork.GetVnic` | `oci_logging://OCI_Audit
TEST1CONAGENT-1` | `ops_non_inf_ocl_m` | `oracle:oci:audit` | `api:oracle:oci:audit` |
| `oracle` | `com.oraclecloud.virtualNetwork.GetVnic` | `oci_logging://OCI_Audit
TEST1CONAGENT-1-New` | `ops_non_inf_ocl_m` | `oracle:oci:audit` | `api:oracle:oci:audit` |
| `oracle` | `com.oraclecloud.virtualNetwork.GetVnic` | `oci_logging://OCI_Audit
TSGTLZ-BASTION-1` | `ops_non_inf_ocl_m` | `oracle:oci:audit` | `api:oracle:oci:audit` |
| `oracle` | `com.oraclecloud.virtualNetwork.GetVnic` | `oci_logging://OCI_Audit
TSGTLZ-PROD-BASTION-1` | `ops_non_inf_ocl_m` | `oracle:oci:audit` | `api:oracle:oci:audit` |
| `oracle` | `com.oraclecloud.virtualNetwork.GetVnic` | `oci_logging://OCI_Audit
Win_Jump_Host` | `ops_non_inf_ocl_m` | `oracle:oci:audit` | `api:oracle:oci:audit` |
| `oracle` | `com.oraclecloud.virtualNetwork.GetVnic` | `oci_logging://OCI_Audit
fss-mnt-{timestamp}` | `ops_non_inf_ocl_m` | `oracle:oci:audit` | `api:oracle:oci:audit` |
| `oracle` | `com.oraclecloud.virtualNetwork.GetVnic` | `oci_logging://OCI_Audit
iam-script-instance` | `ops_non_inf_ocl_m` | `oracle:oci:audit` | `api:oracle:oci:audit` |
| `oracle` | `com.oraclecloud.virtualNetwork.GetVnic` | `oci_logging://OCI_Audit
nsg-ebs-jmp-1` | `ops_non_inf_ocl_m` | `oracle:oci:audit` | `api:oracle:oci:audit` |
| `oracle` | `com.oraclecloud.virtualNetwork.GetVnic` | `oci_logging://OCI_Audit
ocvlcappebs1` | `ops_non_inf_ocl_m` | `oracle:oci:audit` | `api:oracle:oci:audit` |
| `oracle` | `com.oraclecloud.virtualNetwork.GetVnic` | `oci_logging://OCI_Audit
pocvldebsapps` | `ops_non_inf_ocl_m` | `oracle:oci:audit` | `api:oracle:oci:audit` |
| `oracle` | `com.oraclecloud.virtualNetwork.GetVnic` | `oci_logging://OCI_Audit
recovery1_ssl_trombley_2025` | `ops_non_inf_ocl_m` | `oracle:oci:audit` | `api:oracle:oci:audit` |
| `oracle` | `com.oraclecloud.virtualNetwork.GetVnic` | `oci_logging://OCI_Audit
vm-nsg-jump-server` | `ops_non_inf_ocl_m` | `oracle:oci:audit` | `api:oracle:oci:audit` |
| `oracle` | `com.oraclecloud.virtualNetwork.GetVnic` | `oci_logging://OCI_Audit
vm-nsg-jump-server-U42_Review-3-12-25` | `ops_non_inf_ocl_m` | `oracle:oci:audit` | `api:oracle:oci:audit` |
| `oracle` | `com.oraclecloud.virtualNetwork.GetVnic` | `oci_logging://OCI_Audit
vm-oracle-jump-server` | `ops_non_inf_ocl_m` | `oracle:oci:audit` | `api:oracle:oci:audit` |
| `oracle` | `com.oraclecloud.virtualNetwork.GetVnic` | `oci_logging://OCI_Audit
vm-oracle-test` | `ops_non_inf_ocl_m` | `oracle:oci:audit` | `api:oracle:oci:audit` |
| `oracle` | `com.oraclecloud.virtualNetwork.GetVnic` | `oci_logging://OCI_Audit
vnic{timestamp}` | `ops_non_inf_ocl_m` | `oracle:oci:audit` | `api:oracle:oci:audit` |
| `oracle` | `com.oraclecloud.virtualNetwork.ListDhcpOptions` | `oci_logging://OCI_Audit` | `ops_non_inf_ocl_m` | `oracle:oci:audit` | `api:oracle:oci:audit` |
| `oracle` | `com.oraclecloud.virtualNetwork.ListInternalVnics` | `oci_logging://OCI_Audit` | `ops_non_inf_ocl_m` | `oracle:oci:audit` | `api:oracle:oci:audit` |
| `oracle` | `com.oraclecloud.virtualNetwork.ListInternetGateways` | `oci_logging://OCI_Audit` | `ops_non_inf_ocl_m` | `oracle:oci:audit` | `api:oracle:oci:audit` |
| `oracle` | `com.oraclecloud.virtualNetwork.ListLocalPeeringGateways` | `oci_logging://OCI_Audit` | `ops_non_inf_ocl_m` | `oracle:oci:audit` | `api:oracle:oci:audit` |
| `oracle` | `com.oraclecloud.virtualNetwork.ListNetworkSecurityGroupSecurityRules` | `oci_logging://OCI_Audit` | `ops_non_inf_ocl_m` | `oracle:oci:audit` | `api:oracle:oci:audit` |
| `oracle` | `com.oraclecloud.virtualNetwork.ListNetworkSecurityGroups` | `oci_logging://OCI_Audit` | `ops_non_inf_ocl_m` | `oracle:oci:audit` | `api:oracle:oci:audit` |
| `oracle` | `com.oraclecloud.virtualNetwork.ListPrivateIps` | `oci_logging://OCI_Audit` | `ops_non_inf_ocl_m` | `oracle:oci:audit` | `api:oracle:oci:audit` |
| `oracle` | `com.oraclecloud.virtualNetwork.ListRouteTables` | `oci_logging://OCI_Audit` | `ops_non_inf_ocl_m` | `oracle:oci:audit` | `api:oracle:oci:audit` |
| `oracle` | `com.oraclecloud.virtualNetwork.ListSecurityLists` | `oci_logging://OCI_Audit` | `ops_non_inf_ocl_m` | `oracle:oci:audit` | `api:oracle:oci:audit` |
| `oracle` | `com.oraclecloud.virtualNetwork.ListSubnets` | `oci_logging://OCI_Audit` | `ops_non_inf_ocl_m` | `oracle:oci:audit` | `api:oracle:oci:audit` |
| `oracle` | `com.oraclecloud.virtualNetwork.ListVcns` | `oci_logging://OCI_Audit` | `ops_non_inf_ocl_m` | `oracle:oci:audit` | `api:oracle:oci:audit` |
| `oracle` | `oci_logging` | `oci_logging://OCI_Audit` | `ops_non_inf_ocl_m` | `oracle:oci:logging` | `api:oracle:oci:logging` |
| `oracle` | `oci_logging` | `oci_logging://OCI_Audit
/n` | `ops_non_inf_ocl_m` | `oracle:oci:logging` | `api:oracle:oci:logging` |
| `oracle` | `oci_logging` | `oci_logging://OCI_Audit
/n/axeufspbztar/b?compartmentId=ocid1.compartment.oc1..aaaaaaaa2cpn7eaotvowzlgwt6vkgrxx52lc6z7u5u2ip6nr25mn2ev3hkvq&limit=1000&sortBy=NAME&sortOrder=ASC` | `ops_non_inf_ocl_m` | `oracle:oci:logging` | `api:oracle:oci:logging` |
| `oracle` | `oci_logging` | `oci_logging://OCI_Audit
/n/axeufspbztar/b?compartmentId=ocid1.compartment.oc1..aaaaaaaa2no7f7r3t4ts4numhueuxdwhbi2javqypjzfbo3pcz7qberfawrq&limit=1000&sortBy=NAME&sortOrder=ASC` | `ops_non_inf_ocl_m` | `oracle:oci:logging` | `api:oracle:oci:logging` |
| `oracle` | `oci_logging` | `oci_logging://OCI_Audit
/n/axeufspbztar/b?compartmentId=ocid1.compartment.oc1..aaaaaaaa3kgd3x54chb7i3vnnmq72a4cgrackx4a55p7ebi5g2tvfwpf5gca&limit=1000&sortBy=NAME&sortOrder=ASC` | `ops_non_inf_ocl_m` | `oracle:oci:logging` | `api:oracle:oci:logging` |
| `oracle` | `oci_logging` | `oci_logging://OCI_Audit
/n/axeufspbztar/b?compartmentId=ocid1.compartment.oc1..aaaaaaaa3ppro{digits}vgkioyrkqqfvukzfkepd6325a7kxcu37igfsc3gda&limit=1000&sortBy=NAME&sortOrder=ASC` | `ops_non_inf_ocl_m` | `oracle:oci:logging` | `api:oracle:oci:logging` |
| `oracle` | `oci_logging` | `oci_logging://OCI_Audit
/n/axeufspbztar/b?compartmentId=ocid1.compartment.oc1..aaaaaaaa4heu6zwbt5nomag3364s2mgmvomsp345tw7wcc2jejhz67mmmt7a&limit=1000&sortBy=NAME&sortOrder=ASC` | `ops_non_inf_ocl_m` | `oracle:oci:logging` | `api:oracle:oci:logging` |
| `oracle` | `oci_logging` | `oci_logging://OCI_Audit
/n/axeufspbztar/b?compartmentId=ocid1.compartment.oc1..aaaaaaaa4mpdxhzbmici6mejy7prfxtvqmjlmpfwbokuu3xajeye74hgsjta&limit=1000&sortBy=NAME&sortOrder=ASC` | `ops_non_inf_ocl_m` | `oracle:oci:logging` | `api:oracle:oci:logging` |
| `oracle` | `oci_logging` | `oci_logging://OCI_Audit
/n/axeufspbztar/b?compartmentId=ocid1.compartment.oc1..aaaaaaaa4n3ksgt3pj7v7cmwjfntyot4z64dlhw4tohnckipk5fkm4q2hgya&limit=1000&sortBy=NAME&sortOrder=ASC` | `ops_non_inf_ocl_m` | `oracle:oci:logging` | `api:oracle:oci:logging` |
| `oracle` | `oci_logging` | `oci_logging://OCI_Audit
/n/axeufspbztar/b?compartmentId=ocid1.compartment.oc1..aaaaaaaa56wn4nhjms7xbwazbxppq6ffdnrtwx62iv7kgsddi6p3rpnhy65q&limit=1000&sortBy=NAME&sortOrder=ASC` | `ops_non_inf_ocl_m` | `oracle:oci:logging` | `api:oracle:oci:logging` |
| `oracle` | `oci_logging` | `oci_logging://OCI_Audit
/n/axeufspbztar/b?compartmentId=ocid1.compartment.oc1..aaaaaaaa7i5jfys2jsnrcu7mvhrv2l3e5eiaei3r7qqvsl6rbhqs6eddrapa&limit=1000&sortBy=NAME&sortOrder=ASC` | `ops_non_inf_ocl_m` | `oracle:oci:logging` | `api:oracle:oci:logging` |
| `oracle` | `oci_logging` | `oci_logging://OCI_Audit
/n/axeufspbztar/b?compartmentId=ocid1.compartment.oc1..aaaaaaaa7y6yaj3utbhaejnobkiwj3bfqboxfyifhx5ggjdmmlucp7tqt7ja&limit=1000&sortBy=NAME&sortOrder=ASC` | `ops_non_inf_ocl_m` | `oracle:oci:logging` | `api:oracle:oci:logging` |
| `oracle` | `oci_logging` | `oci_logging://OCI_Audit
/n/axeufspbztar/b?compartmentId=ocid1.compartment.oc1..aaaaaaaaa54lfowacelsjab2mn6eitbz6aeoegdvzabvhz2xg6rdes3573ra&limit=1000&sortBy=NAME&sortOrder=ASC` | `ops_non_inf_ocl_m` | `oracle:oci:logging` | `api:oracle:oci:logging` |
| `oracle` | `oci_logging` | `oci_logging://OCI_Audit
/n/axeufspbztar/b?compartmentId=ocid1.compartment.oc1..aaaaaaaabee5spjuxrtp4xukmh6vcszbrrh7fjpcp5vrxvy4ji6zxokvbaoq&limit=1000&sortBy=NAME&sortOrder=ASC` | `ops_non_inf_ocl_m` | `oracle:oci:logging` | `api:oracle:oci:logging` |
| `oracle` | `oci_logging` | `oci_logging://OCI_Audit
/n/axeufspbztar/b?compartmentId=ocid1.compartment.oc1..aaaaaaaad4te2npwia4vxs3bxvawwyog6b6lytb7ng743bou57angrixce2q&limit=1000&sortBy=NAME&sortOrder=ASC` | `ops_non_inf_ocl_m` | `oracle:oci:logging` | `api:oracle:oci:logging` |
| `oracle` | `oci_logging` | `oci_logging://OCI_Audit
/n/axeufspbztar/b?compartmentId=ocid1.compartment.oc1..aaaaaaaaducuqfkwfvfftrcftrtfykm3mpcxjsn2rcuumzerbjkqsnxii6ga&limit=1000&sortBy=NAME&sortOrder=ASC` | `ops_non_inf_ocl_m` | `oracle:oci:logging` | `api:oracle:oci:logging` |
| `oracle` | `oci_logging` | `oci_logging://OCI_Audit
/n/axeufspbztar/b?compartmentId=ocid1.compartment.oc1..aaaaaaaaeowgggkjkmpabke7z23vkoti4mzywivbribtasrtcrkj2c4mjfea&limit=1000&sortBy=NAME&sortOrder=ASC` | `ops_non_inf_ocl_m` | `oracle:oci:logging` | `api:oracle:oci:logging` |
| `oracle` | `oci_logging` | `oci_logging://OCI_Audit
/n/axeufspbztar/b?compartmentId=ocid1.compartment.oc1..aaaaaaaaewarswwkk377dxmop33y6cyghu2w35mdwdlxglgvplg54ml7e2oq&limit=1000&sortBy=NAME&sortOrder=ASC` | `ops_non_inf_ocl_m` | `oracle:oci:logging` | `api:oracle:oci:logging` |
| `oracle` | `oci_logging` | `oci_logging://OCI_Audit
/n/axeufspbztar/b?compartmentId=ocid1.compartment.oc1..aaaaaaaaewpcmj6ldr5qxljqulisd3aeomkinnvarxqdoezwk3ktb5urwtfq&limit=1000&sortBy=NAME&sortOrder=ASC` | `ops_non_inf_ocl_m` | `oracle:oci:logging` | `api:oracle:oci:logging` |
| `oracle` | `oci_logging` | `oci_logging://OCI_Audit
/n/axeufspbztar/b?compartmentId=ocid1.compartment.oc1..aaaaaaaag5eqy7foy4hzi5n3gaefnjvmi7cfurjltgoyukwieu55nbcmsdvq&limit=1000&sortBy=NAME&sortOrder=ASC` | `ops_non_inf_ocl_m` | `oracle:oci:logging` | `api:oracle:oci:logging` |
| `oracle` | `oci_logging` | `oci_logging://OCI_Audit
/n/axeufspbztar/b?compartmentId=ocid1.compartment.oc1..aaaaaaaag7f3qqnnjj5mbhmgblnvlkxoxnd3mwgyobzgvyjhappjswxftcfq&limit=1000&sortBy=NAME&sortOrder=ASC` | `ops_non_inf_ocl_m` | `oracle:oci:logging` | `api:oracle:oci:logging` |
| `oracle` | `oci_logging` | `oci_logging://OCI_Audit
/n/axeufspbztar/b?compartmentId=ocid1.compartment.oc1..aaaaaaaagu7lswmego33g3gflq4vwrapi6d3f3ex2p3u6zgqx2nwom2zl5da&limit=1000&sortBy=NAME&sortOrder=ASC` | `ops_non_inf_ocl_m` | `oracle:oci:logging` | `api:oracle:oci:logging` |
| `oracle` | `oci_logging` | `oci_logging://OCI_Audit
/n/axeufspbztar/b?compartmentId=ocid1.compartment.oc1..aaaaaaaagz7flp44cyph522r3imtcxl3t2yvpdcgedflmgxdfzbdzl6peuva&limit=1000&sortBy=NAME&sortOrder=ASC` | `ops_non_inf_ocl_m` | `oracle:oci:logging` | `api:oracle:oci:logging` |
| `oracle` | `oci_logging` | `oci_logging://OCI_Audit
/n/axeufspbztar/b?compartmentId=ocid1.compartment.oc1..aaaaaaaahcoxkmtkunmqcle77ucbxyqih4agwjaiqkmwl67ykz5vx6bet7pq&limit=1000&sortBy=NAME&sortOrder=ASC` | `ops_non_inf_ocl_m` | `oracle:oci:logging` | `api:oracle:oci:logging` |
| `oracle` | `oci_logging` | `oci_logging://OCI_Audit
/n/axeufspbztar/b?compartmentId=ocid1.compartment.oc1..aaaaaaaai6pk7lvcdzb5zcw7o6ppaklyb4cpacr6xrttvnw7lo35jrszfkoq&limit=1000&sortBy=NAME&sortOrder=ASC` | `ops_non_inf_ocl_m` | `oracle:oci:logging` | `api:oracle:oci:logging` |
| `oracle` | `oci_logging` | `oci_logging://OCI_Audit
/n/axeufspbztar/b?compartmentId=ocid1.compartment.oc1..aaaaaaaaibbk6sprqyyuzyxuayj77mipyzigdey5u456liddrj2tmqknn6bq&limit=1000&sortBy=NAME&sortOrder=ASC` | `ops_non_inf_ocl_m` | `oracle:oci:logging` | `api:oracle:oci:logging` |
| `oracle` | `oci_logging` | `oci_logging://OCI_Audit
/n/axeufspbztar/b?compartmentId=ocid1.compartment.oc1..aaaaaaaaisz7loovuz3niqv6boqrxwx3zvzsvutncahlavmd4jfdsesiunlq&limit=1000&sortBy=NAME&sortOrder=ASC` | `ops_non_inf_ocl_m` | `oracle:oci:logging` | `api:oracle:oci:logging` |
| `oracle` | `oci_logging` | `oci_logging://OCI_Audit
/n/axeufspbztar/b?compartmentId=ocid1.compartment.oc1..aaaaaaaakfh7jh2blxogz5oinr43hrdfem4dqiidosdofuvqwtwzhavbjprq&limit=1000&sortBy=NAME&sortOrder=ASC` | `ops_non_inf_ocl_m` | `oracle:oci:logging` | `api:oracle:oci:logging` |
| `oracle` | `oci_logging` | `oci_logging://OCI_Audit
/n/axeufspbztar/b?compartmentId=ocid1.compartment.oc1..aaaaaaaaklbevghev4ywrdnwh43so4infl5bnkmzvkcn6vj5ojdwvcilrfxq&limit=1000&sortBy=NAME&sortOrder=ASC` | `ops_non_inf_ocl_m` | `oracle:oci:logging` | `api:oracle:oci:logging` |
| `oracle` | `oci_logging` | `oci_logging://OCI_Audit
/n/axeufspbztar/b?compartmentId=ocid1.compartment.oc1..aaaaaaaal44btrbfhti3pidsny3ncxbp2f6hmsboaimg4lqmfss4jfbuhgza&limit=1000&sortBy=NAME&sortOrder=ASC` | `ops_non_inf_ocl_m` | `oracle:oci:logging` | `api:oracle:oci:logging` |
| `oracle` | `oci_logging` | `oci_logging://OCI_Audit
/n/axeufspbztar/b?compartmentId=ocid1.compartment.oc1..aaaaaaaal6azbq2wfijfj5txhanmwfcu7sbojqeto5uimfamvtonbv4g7iwa&limit=1000&sortBy=NAME&sortOrder=ASC` | `ops_non_inf_ocl_m` | `oracle:oci:logging` | `api:oracle:oci:logging` |
| `oracle` | `oci_logging` | `oci_logging://OCI_Audit
/n/axeufspbztar/b?compartmentId=ocid1.compartment.oc1..aaaaaaaans3jk4xsrbccox2ffl33qqgb7wurwri77cheps4iqw27x2p7jnka&limit=1000&sortBy=NAME&sortOrder=ASC` | `ops_non_inf_ocl_m` | `oracle:oci:logging` | `api:oracle:oci:logging` |
| `oracle` | `oci_logging` | `oci_logging://OCI_Audit
/n/axeufspbztar/b?compartmentId=ocid1.compartment.oc1..aaaaaaaapdj6ukebgt2uvlhxikqbzrql6yoabdytqqzcrmaspt7kvj64srdq&limit=1000&sortBy=NAME&sortOrder=ASC` | `ops_non_inf_ocl_m` | `oracle:oci:logging` | `api:oracle:oci:logging` |
| `oracle` | `oci_logging` | `oci_logging://OCI_Audit
/n/axeufspbztar/b?compartmentId=ocid1.compartment.oc1..aaaaaaaaqbfvsippn33lotx6w277xk3cs46n4vbvjciq5gx5pywpw26bsm2a&fields=tags&limit=1000&sortBy=name&sortOrder=ASC` | `ops_non_inf_ocl_m` | `oracle:oci:logging` | `api:oracle:oci:logging` |
| `oracle` | `oci_logging` | `oci_logging://OCI_Audit
/n/axeufspbztar/b?compartmentId=ocid1.compartment.oc1..aaaaaaaaqbfvsippn33lotx6w277xk3cs46n4vbvjciq5gx5pywpw26bsm2a&limit=1000&sortBy=NAME&sortOrder=ASC` | `ops_non_inf_ocl_m` | `oracle:oci:logging` | `api:oracle:oci:logging` |
| `oracle` | `oci_logging` | `oci_logging://OCI_Audit
/n/axeufspbztar/b?compartmentId=ocid1.compartment.oc1..aaaaaaaaqrq7f2mm5xpxksmneed3uiao7bi5j3bzvd4pjp455rsxsaend4ta&limit=1000&sortBy=NAME&sortOrder=ASC` | `ops_non_inf_ocl_m` | `oracle:oci:logging` | `api:oracle:oci:logging` |
| `oracle` | `oci_logging` | `oci_logging://OCI_Audit
/n/axeufspbztar/b?compartmentId=ocid1.compartment.oc1..aaaaaaaarnqf2j7jyxzud66zsazcbh3wgdlhshll73bk5qcqidxbvmdi2dwa&limit=1000&sortBy=NAME&sortOrder=ASC` | `ops_non_inf_ocl_m` | `oracle:oci:logging` | `api:oracle:oci:logging` |
| `oracle` | `oci_logging` | `oci_logging://OCI_Audit
/n/axeufspbztar/b?compartmentId=ocid1.compartment.oc1..aaaaaaaasthbynwbsebsrqnph2ggdfbtfaqrpuzwkdu6ihf3palfool4qcha&limit=1000&sortBy=NAME&sortOrder=ASC` | `ops_non_inf_ocl_m` | `oracle:oci:logging` | `api:oracle:oci:logging` |
| `oracle` | `oci_logging` | `oci_logging://OCI_Audit
/n/axeufspbztar/b?compartmentId=ocid1.compartment.oc1..aaaaaaaat4mb7kmdkmgpb27mlthzyc6jjziys6edklyv24wic37ptyjeuw7a&limit=1000&sortBy=NAME&sortOrder=ASC` | `ops_non_inf_ocl_m` | `oracle:oci:logging` | `api:oracle:oci:logging` |
| `oracle` | `oci_logging` | `oci_logging://OCI_Audit
/n/axeufspbztar/b?compartmentId=ocid1.compartment.oc1..aaaaaaaatm4kifkwuund3duazaqwip7bulj5ge32x7747ak5qio3d3ckx7oa&limit=1000&sortBy=NAME&sortOrder=ASC` | `ops_non_inf_ocl_m` | `oracle:oci:logging` | `api:oracle:oci:logging` |
| `oracle` | `oci_logging` | `oci_logging://OCI_Audit
/n/axeufspbztar/b?compartmentId=ocid1.compartment.oc1..aaaaaaaatqdnsywm4p5dhhsdg24pnbv5iwq4o4xlj2f5imjvtpamo2jbay7q&limit=1000&sortBy=NAME&sortOrder=ASC` | `ops_non_inf_ocl_m` | `oracle:oci:logging` | `api:oracle:oci:logging` |
| `oracle` | `oci_logging` | `oci_logging://OCI_Audit
/n/axeufspbztar/b?compartmentId=ocid1.compartment.oc1..aaaaaaaatu3mu57ygk3pihmq4aklunvdhednriqzskbky6pl4cile6p4dkma&limit=1000&sortBy=NAME&sortOrder=ASC` | `ops_non_inf_ocl_m` | `oracle:oci:logging` | `api:oracle:oci:logging` |
| `oracle` | `oci_logging` | `oci_logging://OCI_Audit
/n/axeufspbztar/b?compartmentId=ocid1.compartment.oc1..aaaaaaaaumbccqiwiksl6qgycgcuihl63dbgzhabcssfo7kkgif7b4beopca&limit=1000&sortBy=NAME&sortOrder=ASC` | `ops_non_inf_ocl_m` | `oracle:oci:logging` | `api:oracle:oci:logging` |
| `oracle` | `oci_logging` | `oci_logging://OCI_Audit
/n/axeufspbztar/b?compartmentId=ocid1.compartment.oc1..aaaaaaaauvsary7s4boitrozzbjizvaiohrlbgc2t5puxnd3w3ip2pjcd5ja&limit=1000&sortBy=NAME&sortOrder=ASC` | `ops_non_inf_ocl_m` | `oracle:oci:logging` | `api:oracle:oci:logging` |
| `oracle` | `oci_logging` | `oci_logging://OCI_Audit
/n/axeufspbztar/b?compartmentId=ocid1.compartment.oc1..aaaaaaaauy4l26lle6yepkeewc6i7malrmhepqkyv2mwwtafx2ajxczw2rta&limit=1000&sortBy=NAME&sortOrder=ASC` | `ops_non_inf_ocl_m` | `oracle:oci:logging` | `api:oracle:oci:logging` |
| `oracle` | `oci_logging` | `oci_logging://OCI_Audit
/n/axeufspbztar/b?compartmentId=ocid1.compartment.oc1..aaaaaaaawnzugdmltz4pp3qnljhu2lqvytao2xzkkz4oyaf5hxnqox6lhtyq&limit=1000&sortBy=NAME&sortOrder=ASC` | `ops_non_inf_ocl_m` | `oracle:oci:logging` | `api:oracle:oci:logging` |
| `oracle` | `oci_logging` | `oci_logging://OCI_Audit
/n/axeufspbztar/b?compartmentId=ocid1.compartment.oc1..aaaaaaaawy{digits}g56wuhofepjnbb5gjmhzy6ahpcflgzr4dqnxewtqt4jq&limit=1000&sortBy=NAME&sortOrder=ASC` | `ops_non_inf_ocl_m` | `oracle:oci:logging` | `api:oracle:oci:logging` |
| `oracle` | `oci_logging` | `oci_logging://OCI_Audit
/n/axeufspbztar/b?compartmentId=ocid1.compartment.oc1..aaaaaaaaxxdr2gyz6xvph6q7snueu5voks4b5mpgvir52hxniaybzfhy7jkq&limit=1000&sortBy=NAME&sortOrder=ASC` | `ops_non_inf_ocl_m` | `oracle:oci:logging` | `api:oracle:oci:logging` |
| `oracle` | `oci_logging` | `oci_logging://OCI_Audit
/n/axeufspbztar/b?compartmentId=ocid1.compartment.oc1..aaaaaaaayglqtwyrxn7regptmosldekp4sebygsw75qfnpf2vd5g22ledwca&limit=1000&sortBy=NAME&sortOrder=ASC` | `ops_non_inf_ocl_m` | `oracle:oci:logging` | `api:oracle:oci:logging` |
| `oracle` | `oci_logging` | `oci_logging://OCI_Audit
/n/axeufspbztar/b?compartmentId=ocid1.compartment.oc1..aaaaaaaaypaglfu4r76bduahg3sreejxoe3d7wkw5csptessjcpbjioh2o3a&limit=1000&sortBy=NAME&sortOrder=ASC` | `ops_non_inf_ocl_m` | `oracle:oci:logging` | `api:oracle:oci:logging` |
| `oracle` | `oci_logging` | `oci_logging://OCI_Audit
/n/axeufspbztar/b?compartmentId=ocid1.compartment.oc1..aaaaaaaazdepo2wthedcc442aswxvfmh3fhkahy4k2eaqan7bnw3bx6shsiq&limit=1000&sortBy=NAME&sortOrder=ASC` | `ops_non_inf_ocl_m` | `oracle:oci:logging` | `api:oracle:oci:logging` |
| `oracle` | `oci_logging` | `oci_logging://OCI_Audit
/n/axeufspbztar/b?compartmentId=ocid1.tenancy.oc1..aaaaaaaatfhve2vbquaz6dbrl6jf2gbz6k7pp6cfjoqbjf2kbwaf63b6c7za&limit=1000&sortBy=NAME&sortOrder=ASC` | `ops_non_inf_ocl_m` | `oracle:oci:logging` | `api:oracle:oci:logging` |
| `oracle` | `oci_logging` | `oci_logging://OCI_Audit
3a{digits}ae{digits}f80c{digits}d0f_AP_POET_CORRECTION_USER/AP_POET_CORRECTION_USER` | `ops_non_inf_ocl_m` | `oracle:oci:logging` | `api:oracle:oci:logging` |
| `oracle` | `oci_logging` | `oci_logging://OCI_Audit
69b{digits}fad{digits}e077e08e8c2be75_AP_POET_CORRECTION_USER/AP_POET_CORRECTION_USER` | `ops_non_inf_ocl_m` | `oracle:oci:logging` | `api:oracle:oci:logging` |
| `oracle` | `oci_logging` | `oci_logging://OCI_Audit
82f9c1d363c940e59eb{digits}e658e04e_AP_POET_CORRECTION_USER/AP_POET_CORRECTION_USER` | `ops_non_inf_ocl_m` | `oracle:oci:logging` | `api:oracle:oci:logging` |
| `oracle` | `oci_logging` | `oci_logging://OCI_Audit
911ce{digits}c96c049cee797b24f_AP_POET_CORRECTION_USER/AP_POET_CORRECTION_USER` | `ops_non_inf_ocl_m` | `oracle:oci:logging` | `api:oracle:oci:logging` |
| `oracle` | `oci_logging` | `oci_logging://OCI_Audit
APEX-TEST` | `ops_non_inf_ocl_m` | `oracle:oci:logging` | `api:oracle:oci:logging` |
| `oracle` | `oci_logging` | `oci_logging://OCI_Audit
AccountMgmtInfo` | `ops_non_inf_ocl_m` | `oracle:oci:logging` | `api:oracle:oci:logging` |
| `oracle` | `oci_logging` | `oci_logging://OCI_Audit
AppRole` | `ops_non_inf_ocl_m` | `oracle:oci:logging` | `api:oracle:oci:logging` |
| `oracle` | `oci_logging` | `oci_logging://OCI_Audit
Archivebucket` | `ops_non_inf_ocl_m` | `oracle:oci:logging` | `api:oracle:oci:logging` |
| `oracle` | `oci_logging` | `oci_logging://OCI_Audit
Archivebucket_PROD` | `ops_non_inf_ocl_m` | `oracle:oci:logging` | `api:oracle:oci:logging` |
| `oracle` | `oci_logging` | `oci_logging://OCI_Audit
Archivebucket_TEST` | `ops_non_inf_ocl_m` | `oracle:oci:logging` | `api:oracle:oci:logging` |
| `oracle` | `oci_logging` | `oci_logging://OCI_Audit
Attachment-PROD` | `ops_non_inf_ocl_m` | `oracle:oci:logging` | `api:oracle:oci:logging` |
| `oracle` | `oci_logging` | `oci_logging://OCI_Audit
Aug 18, 2026 09:04:12 UTC` | `ops_non_inf_ocl_m` | `oracle:oci:logging` | `api:oracle:oci:logging` |
| `oracle` | `oci_logging` | `oci_logging://OCI_Audit
Aug 18, 2026 10:11:37 UTC` | `ops_non_inf_ocl_m` | `oracle:oci:logging` | `api:oracle:oci:logging` |
| `oracle` | `oci_logging` | `oci_logging://OCI_Audit
Aug 18, 2026 12:38:34 UTC` | `ops_non_inf_ocl_m` | `oracle:oci:logging` | `api:oracle:oci:logging` |
| `oracle` | `oci_logging` | `oci_logging://OCI_Audit
Aug 18, 2026 13:52:26 UTC` | `ops_non_inf_ocl_m` | `oracle:oci:logging` | `api:oracle:oci:logging` |
| `oracle` | `oci_logging` | `oci_logging://OCI_Audit
Aug 18, 2026 16:53:17 UTC` | `ops_non_inf_ocl_m` | `oracle:oci:logging` | `api:oracle:oci:logging` |
| `oracle` | `oci_logging` | `oci_logging://OCI_Audit
Aug 18, 2026 17:52:55 UTC` | `ops_non_inf_ocl_m` | `oracle:oci:logging` | `api:oracle:oci:logging` |
| `oracle` | `oci_logging` | `oci_logging://OCI_Audit
BKP_DB_OH_{digits}` | `ops_non_inf_ocl_m` | `oracle:oci:logging` | `api:oracle:oci:logging` |
| `oracle` | `oci_logging` | `oci_logging://OCI_Audit
CMA-Files` | `ops_non_inf_ocl_m` | `oracle:oci:logging` | `api:oracle:oci:logging` |
| `oracle` | `oci_logging` | `oci_logging://OCI_Audit
CONV-Export` | `ops_non_inf_ocl_m` | `oracle:oci:logging` | `api:oracle:oci:logging` |
| `oracle` | `oci_logging` | `oci_logging://OCI_Audit
CONV-Import` | `ops_non_inf_ocl_m` | `oracle:oci:logging` | `api:oracle:oci:logging` |
| `oracle` | `oci_logging` | `oci_logging://OCI_Audit
Cority.Medgate_meip` | `ops_non_inf_ocl_m` | `oracle:oci:logging` | `api:oracle:oci:logging` |
| `oracle` | `oci_logging` | `oci_logging://OCI_Audit
DEV-FILES-SAMPLE` | `ops_non_inf_ocl_m` | `oracle:oci:logging` | `api:oracle:oci:logging` |
| `oracle` | `oci_logging` | `oci_logging://OCI_Audit
Default DHCP Options for TSGTLZVCN` | `ops_non_inf_ocl_m` | `oracle:oci:logging` | `api:oracle:oci:logging` |
| `oracle` | `oci_logging` | `oci_logging://OCI_Audit
Domain` | `ops_non_inf_ocl_m` | `oracle:oci:logging` | `api:oracle:oci:logging` |
| `oracle` | `oci_logging` | `oci_logging://OCI_Audit
EBSMIGBCKT` | `ops_non_inf_ocl_m` | `oracle:oci:logging` | `api:oracle:oci:logging` |
| `oracle` | `oci_logging` | `oci_logging://OCI_Audit
EBSPROD` | `ops_non_inf_ocl_m` | `oracle:oci:logging` | `api:oracle:oci:logging` |
| `oracle` | `oci_logging` | `oci_logging://OCI_Audit
ERP-Batch-PROD` | `ops_non_inf_ocl_m` | `oracle:oci:logging` | `api:oracle:oci:logging` |
| `oracle` | `oci_logging` | `oci_logging://OCI_Audit
ERP-Batch-PROD-Archive` | `ops_non_inf_ocl_m` | `oracle:oci:logging` | `api:oracle:oci:logging` |
| `oracle` | `oci_logging` | `oci_logging://OCI_Audit
ERP-Batch-PROD-Error` | `ops_non_inf_ocl_m` | `oracle:oci:logging` | `api:oracle:oci:logging` |
| `oracle` | `oci_logging` | `oci_logging://OCI_Audit
ERP-Report-PROD` | `ops_non_inf_ocl_m` | `oracle:oci:logging` | `api:oracle:oci:logging` |
| `oracle` | `oci_logging` | `oci_logging://OCI_Audit
ERP_Assets_Extract` | `ops_non_inf_ocl_m` | `oracle:oci:logging` | `api:oracle:oci:logging` |
| `oracle` | `oci_logging` | `oci_logging://OCI_Audit
Enrichedbucket` | `ops_non_inf_ocl_m` | `oracle:oci:logging` | `api:oracle:oci:logging` |
| `oracle` | `oci_logging` | `oci_logging://OCI_Audit
Enrichedbucket_PROD` | `ops_non_inf_ocl_m` | `oracle:oci:logging` | `api:oracle:oci:logging` |
| `oracle` | `oci_logging` | `oci_logging://OCI_Audit
Enrichedbucket_TEST` | `ops_non_inf_ocl_m` | `oracle:oci:logging` | `api:oracle:oci:logging` |
| `oracle` | `oci_logging` | `oci_logging://OCI_Audit
Errorbucket` | `ops_non_inf_ocl_m` | `oracle:oci:logging` | `api:oracle:oci:logging` |
| `oracle` | `oci_logging` | `oci_logging://OCI_Audit
Errorbucket_PROD` | `ops_non_inf_ocl_m` | `oracle:oci:logging` | `api:oracle:oci:logging` |
| `oracle` | `oci_logging` | `oci_logging://OCI_Audit
Errorbucket_TEST` | `ops_non_inf_ocl_m` | `oracle:oci:logging` | `api:oracle:oci:logging` |
| `oracle` | `oci_logging` | `oci_logging://OCI_Audit
FA-Extract-PROD` | `ops_non_inf_ocl_m` | `oracle:oci:logging` | `api:oracle:oci:logging` |
| `oracle` | `oci_logging` | `oci_logging://OCI_Audit
Grant` | `ops_non_inf_ocl_m` | `oracle:oci:logging` | `api:oracle:oci:logging` |
| `oracle` | `oci_logging` | `oci_logging://OCI_Audit
Jun 19, 2026 11:08:34 UTC` | `ops_non_inf_ocl_m` | `oracle:oci:logging` | `api:oracle:oci:logging` |
| `oracle` | `oci_logging` | `oci_logging://OCI_Audit
Jun 19, 2026 13:12:14 UTC` | `ops_non_inf_ocl_m` | `oracle:oci:logging` | `api:oracle:oci:logging` |
| `oracle` | `oci_logging` | `oci_logging://OCI_Audit
Jun 19, 2026 17:26:40 UTC` | `ops_non_inf_ocl_m` | `oracle:oci:logging` | `api:oracle:oci:logging` |
| `oracle` | `oci_logging` | `oci_logging://OCI_Audit
Jun 19, 2026 18:08:42 UTC` | `ops_non_inf_ocl_m` | `oracle:oci:logging` | `api:oracle:oci:logging` |
| `oracle` | `oci_logging` | `oci_logging://OCI_Audit
NP-PIF-ARCHIVE` | `ops_non_inf_ocl_m` | `oracle:oci:logging` | `api:oracle:oci:logging` |
| `oracle` | `oci_logging` | `oci_logging://OCI_Audit
NP-PIF-Integration` | `ops_non_inf_ocl_m` | `oracle:oci:logging` | `api:oracle:oci:logging` |
| `oracle` | `oci_logging` | `oci_logging://OCI_Audit
OIC-Export` | `ops_non_inf_ocl_m` | `oracle:oci:logging` | `api:oracle:oci:logging` |
| `oracle` | `oci_logging` | `oci_logging://OCI_Audit
OKIT Network Diagram Discovery` | `ops_non_inf_ocl_m` | `oracle:oci:logging` | `api:oracle:oci:logging` |
| `oracle` | `oci_logging` | `oci_logging://OCI_Audit
OKIT_Network_Diagram_Read_Tenant` | `ops_non_inf_ocl_m` | `oracle:oci:logging` | `api:oracle:oci:logging` |
| `oracle` | `oci_logging` | `oci_logging://OCI_Audit
PIF-Integration-PROD` | `ops_non_inf_ocl_m` | `oracle:oci:logging` | `api:oracle:oci:logging` |
| `oracle` | `oci_logging` | `oci_logging://OCI_Audit
PPM-Dev-Batch` | `ops_non_inf_ocl_m` | `oracle:oci:logging` | `api:oracle:oci:logging` |
| `oracle` | `oci_logging` | `oci_logging://OCI_Audit
PPM-Dev-Batch_Archive` | `ops_non_inf_ocl_m` | `oracle:oci:logging` | `api:oracle:oci:logging` |
| `oracle` | `oci_logging` | `oci_logging://OCI_Audit
PPM-Dev-Batch_Error` | `ops_non_inf_ocl_m` | `oracle:oci:logging` | `api:oracle:oci:logging` |
| `oracle` | `oci_logging` | `oci_logging://OCI_Audit
PPM-Test-Batch` | `ops_non_inf_ocl_m` | `oracle:oci:logging` | `api:oracle:oci:logging` |
| `oracle` | `oci_logging` | `oci_logging://OCI_Audit
PPM-Test-Batch_Archive` | `ops_non_inf_ocl_m` | `oracle:oci:logging` | `api:oracle:oci:logging` |
| `oracle` | `oci_logging` | `oci_logging://OCI_Audit
PPM-Test-Batch_Error` | `ops_non_inf_ocl_m` | `oracle:oci:logging` | `api:oracle:oci:logging` |
| `oracle` | `oci_logging` | `oci_logging://OCI_Audit
PPM-Test01-Batch` | `ops_non_inf_ocl_m` | `oracle:oci:logging` | `api:oracle:oci:logging` |
| `oracle` | `oci_logging` | `oci_logging://OCI_Audit
PPM-Test01-Batch_Archive` | `ops_non_inf_ocl_m` | `oracle:oci:logging` | `api:oracle:oci:logging` |
| `oracle` | `oci_logging` | `oci_logging://OCI_Audit
PPM-Test01-Batch_Error` | `ops_non_inf_ocl_m` | `oracle:oci:logging` | `api:oracle:oci:logging` |
| `oracle` | `oci_logging` | `oci_logging://OCI_Audit
PROD-PIF-ARCHIVE` | `ops_non_inf_ocl_m` | `oracle:oci:logging` | `api:oracle:oci:logging` |
| `oracle` | `oci_logging` | `oci_logging://OCI_Audit
PROD-PIF-Integration` | `ops_non_inf_ocl_m` | `oracle:oci:logging` | `api:oracle:oci:logging` |
| `oracle` | `oci_logging` | `oci_logging://OCI_Audit
Planning EPM FinDev Test Power User` | `ops_non_inf_ocl_m` | `oracle:oci:logging` | `api:oracle:oci:logging` |
| `oracle` | `oci_logging` | `oci_logging://OCI_Audit
Policy` | `ops_non_inf_ocl_m` | `oracle:oci:logging` | `api:oracle:oci:logging` |
| `oracle` | `oci_logging` | `oci_logging://OCI_Audit
Powerbase.svc_pbapi_ocprod` | `ops_non_inf_ocl_m` | `oracle:oci:logging` | `api:oracle:oci:logging` |
| `oracle` | `oci_logging` | `oci_logging://OCI_Audit
Powerbase.svc_pbapi_octest` | `ops_non_inf_ocl_m` | `oracle:oci:logging` | `api:oracle:oci:logging` |
| `oracle` | `oci_logging` | `oci_logging://OCI_Audit
Processedbucket` | `ops_non_inf_ocl_m` | `oracle:oci:logging` | `api:oracle:oci:logging` |
| `oracle` | `oci_logging` | `oci_logging://OCI_Audit
Processedbucket_PROD` | `ops_non_inf_ocl_m` | `oracle:oci:logging` | `api:oracle:oci:logging` |
| `oracle` | `oci_logging` | `oci_logging://OCI_Audit
Processedbucket_TEST` | `ops_non_inf_ocl_m` | `oracle:oci:logging` | `api:oracle:oci:logging` |
| `oracle` | `oci_logging` | `oci_logging://OCI_Audit
REPORT-TEST` | `ops_non_inf_ocl_m` | `oracle:oci:logging` | `api:oracle:oci:logging` |
| `oracle` | `oci_logging` | `oci_logging://OCI_Audit
Rawbucket` | `ops_non_inf_ocl_m` | `oracle:oci:logging` | `api:oracle:oci:logging` |
| `oracle` | `oci_logging` | `oci_logging://OCI_Audit
Rawbucket_PROD` | `ops_non_inf_ocl_m` | `oracle:oci:logging` | `api:oracle:oci:logging` |
| `oracle` | `oci_logging` | `oci_logging://OCI_Audit
Rawbucket_TEST` | `ops_non_inf_ocl_m` | `oracle:oci:logging` | `api:oracle:oci:logging` |
| `oracle` | `oci_logging` | `oci_logging://OCI_Audit
SaaS_Service_Accounts_MFA_Disabled` | `ops_non_inf_ocl_m` | `oracle:oci:logging` | `api:oracle:oci:logging` |
| `oracle` | `oci_logging` | `oci_logging://OCI_Audit
Service Accounts - SaaS Applications` | `ops_non_inf_ocl_m` | `oracle:oci:logging` | `api:oracle:oci:logging` |
| `oracle` | `oci_logging` | `oci_logging://OCI_Audit
TOA-Files` | `ops_non_inf_ocl_m` | `oracle:oci:logging` | `api:oracle:oci:logging` |
| `oracle` | `oci_logging` | `oci_logging://OCI_Audit
TOA4-PROD` | `ops_non_inf_ocl_m` | `oracle:oci:logging` | `api:oracle:oci:logging` |
| `oracle` | `oci_logging` | `oci_logging://OCI_Audit
TOA4-TestData` | `ops_non_inf_ocl_m` | `oracle:oci:logging` | `api:oracle:oci:logging` |
| `oracle` | `oci_logging` | `oci_logging://OCI_Audit
TOA4-UAT` | `ops_non_inf_ocl_m` | `oracle:oci:logging` | `api:oracle:oci:logging` |
| `oracle` | `oci_logging` | `oci_logging://OCI_Audit
TSGTLZ-appdev-bucket` | `ops_non_inf_ocl_m` | `oracle:oci:logging` | `api:oracle:oci:logging` |
| `oracle` | `oci_logging` | `oci_logging://OCI_Audit
TSGTLZVCN-web-subnet_192.168.224.0_24` | `ops_non_inf_ocl_m` | `oracle:oci:logging` | `api:oracle:oci:logging` |
| `oracle` | `oci_logging` | `oci_logging://OCI_Audit
TSGT_OIC_HOME` | `ops_non_inf_ocl_m` | `oracle:oci:logging` | `api:oracle:oci:logging` |
| `oracle` | `oci_logging` | `oci_logging://OCI_Audit
TSGT_Vault01_NonProd_USWest` | `ops_non_inf_ocl_m` | `oracle:oci:logging` | `api:oracle:oci:logging` |
| `oracle` | `oci_logging` | `oci_logging://OCI_Audit
TSGT_Vault01_Prod_USWest` | `ops_non_inf_ocl_m` | `oracle:oci:logging` | `api:oracle:oci:logging` |
| `oracle` | `oci_logging` | `oci_logging://OCI_Audit
TSGT_Vault01_USWest` | `ops_non_inf_ocl_m` | `oracle:oci:logging` | `api:oracle:oci:logging` |
| `oracle` | `oci_logging` | `oci_logging://OCI_Audit
Unifier-DEV-AssetExtract` | `ops_non_inf_ocl_m` | `oracle:oci:logging` | `api:oracle:oci:logging` |
| `oracle` | `oci_logging` | `oci_logging://OCI_Audit
Upload-Test` | `ops_non_inf_ocl_m` | `oracle:oci:logging` | `api:oracle:oci:logging` |
| `oracle` | `oci_logging` | `oci_logging://OCI_Audit
User` | `ops_non_inf_ocl_m` | `oracle:oci:logging` | `api:oracle:oci:logging` |
| `oracle` | `oci_logging` | `oci_logging://OCI_Audit
VizOCI-graphs` | `ops_non_inf_ocl_m` | `oracle:oci:logging` | `api:oracle:oci:logging` |
| `oracle` | `oci_logging` | `oci_logging://OCI_Audit
WACS-ERP_Assets_Cloud_Extract` | `ops_non_inf_ocl_m` | `oracle:oci:logging` | `api:oracle:oci:logging` |
| `oracle` | `oci_logging` | `oci_logging://OCI_Audit
WACS-TEST03-CM-REPRTUE` | `ops_non_inf_ocl_m` | `oracle:oci:logging` | `api:oracle:oci:logging` |
| `oracle` | `oci_logging` | `oci_logging://OCI_Audit
WACS-TEST03-CM-WAREHOUSE` | `ops_non_inf_ocl_m` | `oracle:oci:logging` | `api:oracle:oci:logging` |
| `oracle` | `oci_logging` | `oci_logging://OCI_Audit
analytics_transmission_storage_bucket_dev` | `ops_non_inf_ocl_m` | `oracle:oci:logging` | `api:oracle:oci:logging` |
| `oracle` | `oci_logging` | `oci_logging://OCI_Audit
analytics_transmission_storage_bucket_prod` | `ops_non_inf_ocl_m` | `oracle:oci:logging` | `api:oracle:oci:logging` |
| `oracle` | `oci_logging` | `oci_logging://OCI_Audit
analytics_transmission_storage_bucket_test` | `ops_non_inf_ocl_m` | `oracle:oci:logging` | `api:oracle:oci:logging` |
| `oracle` | `oci_logging` | `oci_logging://OCI_Audit
bucket-{digits}-1632` | `ops_non_inf_ocl_m` | `oracle:oci:logging` | `api:oracle:oci:logging` |
| `oracle` | `oci_logging` | `oci_logging://OCI_Audit
bucket-{digits}-1656` | `ops_non_inf_ocl_m` | `oracle:oci:logging` | `api:oracle:oci:logging` |
| `oracle` | `oci_logging` | `oci_logging://OCI_Audit
dbhome{timestamp}` | `ops_non_inf_ocl_m` | `oracle:oci:logging` | `api:oracle:oci:logging` |
| `oracle` | `oci_logging` | `oci_logging://OCI_Audit
ebs1` | `ops_non_inf_ocl_m` | `oracle:oci:logging` | `api:oracle:oci:logging` |
| `oracle` | `oci_logging` | `oci_logging://OCI_Audit
employee-sync-dev` | `ops_non_inf_ocl_m` | `oracle:oci:logging` | `api:oracle:oci:logging` |
| `oracle` | `oci_logging` | `oci_logging://OCI_Audit
employee-sync-dev-arch` | `ops_non_inf_ocl_m` | `oracle:oci:logging` | `api:oracle:oci:logging` |
| `oracle` | `oci_logging` | `oci_logging://OCI_Audit
fa-extract-dev` | `ops_non_inf_ocl_m` | `oracle:oci:logging` | `api:oracle:oci:logging` |
| `oracle` | `oci_logging` | `oci_logging://OCI_Audit
migration` | `ops_non_inf_ocl_m` | `oracle:oci:logging` | `api:oracle:oci:logging` |
| `oracle` | `oci_logging` | `oci_logging://OCI_Audit
oax-TSGTFAWProd` | `ops_non_inf_ocl_m` | `oracle:oci:logging` | `api:oracle:oci:logging` |
| `oracle` | `oci_logging` | `oci_logging://OCI_Audit
oax-TSGTFDIDev2` | `ops_non_inf_ocl_m` | `oracle:oci:logging` | `api:oracle:oci:logging` |
| `oracle` | `oci_logging` | `oci_logging://OCI_Audit
privateip for API Gateway ocid1.apigateway.oc1.phx.amaaaaaaylygzbqaggqmtretac5bpqsyscblvto5nyq54mlwfr6tuzhg5dgq` | `ops_non_inf_ocl_m` | `oracle:oci:logging` | `api:oracle:oci:logging` |
| `oracle` | `oci_logging` | `oci_logging://OCI_Audit
privateip for API Gateway ocid1.apigateway.oc1.phx.amaaaaaaylygzbqajbvg3eu5xxuwgn3uow4nuna7wf4lsimxmljenvk336ra` | `ops_non_inf_ocl_m` | `oracle:oci:logging` | `api:oracle:oci:logging` |
| `oracle` | `oci_logging` | `oci_logging://OCI_Audit
publicip for API Gateway ocid1.apigateway.oc1.phx.amaaaaaaylygzbqaggqmtretac5bpqsyscblvto5nyq54mlwfr6tuzhg5dgq` | `ops_non_inf_ocl_m` | `oracle:oci:logging` | `api:oracle:oci:logging` |
| `oracle` | `oci_logging` | `oci_logging://OCI_Audit
publicip for API Gateway ocid1.apigateway.oc1.phx.amaaaaaaylygzbqajbvg3eu5xxuwgn3uow4nuna7wf4lsimxmljenvk336ra` | `ops_non_inf_ocl_m` | `oracle:oci:logging` | `api:oracle:oci:logging` |
| `oracle` | `oci_logging` | `oci_logging://OCI_Audit
servicehistory-prod` | `ops_non_inf_ocl_m` | `oracle:oci:logging` | `api:oracle:oci:logging` |
| `oracle` | `oci_logging` | `oci_logging://OCI_Audit
servicehistory-test` | `ops_non_inf_ocl_m` | `oracle:oci:logging` | `api:oracle:oci:logging` |
| `oracle` | `oci_logging` | `oci_logging://OCI_Audit
shajoh` | `ops_non_inf_ocl_m` | `oracle:oci:logging` | `api:oracle:oci:logging` |
| `oracle` | `oci_logging` | `oci_logging://OCI_Audit
srw-testing-oic` | `ops_non_inf_ocl_m` | `oracle:oci:logging` | `api:oracle:oci:logging` |
| `oracle` | `oci_logging` | `oci_logging://OCI_Audit
svc_oci_network_diagram` | `ops_non_inf_ocl_m` | `oracle:oci:logging` | `api:oracle:oci:logging` |
| `oracle` | `oci_logging` | `oci_logging://OCI_Audit
user_12d{digits}@example.invalid` | `ops_non_inf_ocl_m` | `oracle:oci:logging` | `api:oracle:oci:logging` |
| `oracle` | `oci_logging` | `oci_logging://OCI_Audit
user_2e8f6228@example.invalid` | `ops_non_inf_ocl_m` | `oracle:oci:logging` | `api:oracle:oci:logging` |
| `oracle` | `oci_logging` | `oci_logging://OCI_Audit
user_48eccef0@example.invalid` | `ops_non_inf_ocl_m` | `oracle:oci:logging` | `api:oracle:oci:logging` |
| `oracle` | `oci_logging` | `oci_logging://OCI_Audit
user_4a7d0742@example.invalid` | `ops_non_inf_ocl_m` | `oracle:oci:logging` | `api:oracle:oci:logging` |
| `oracle` | `oci_logging` | `oci_logging://OCI_Audit
user_4b855ea8@example.invalid` | `ops_non_inf_ocl_m` | `oracle:oci:logging` | `api:oracle:oci:logging` |
| `oracle` | `oci_logging` | `oci_logging://OCI_Audit
user_917afd95@example.invalid` | `ops_non_inf_ocl_m` | `oracle:oci:logging` | `api:oracle:oci:logging` |
| `oracle` | `oci_logging` | `oci_logging://OCI_Audit
user_{digits}@example.invalid` | `ops_non_inf_ocl_m` | `oracle:oci:logging` | `api:oracle:oci:logging` |
| `oracle` | `oci_logging` | `oci_logging://OCI_Audit
vehicle-usage-PROD` | `ops_non_inf_ocl_m` | `oracle:oci:logging` | `api:oracle:oci:logging` |
| `oracle` | `oci_logging` | `oci_logging://OCI_Audit
vehicle-usage-PROD-arch` | `ops_non_inf_ocl_m` | `oracle:oci:logging` | `api:oracle:oci:logging` |
| `oracle` | `oci_logging` | `oci_logging://OCI_Audit
vehicle-usage-PROD-error` | `ops_non_inf_ocl_m` | `oracle:oci:logging` | `api:oracle:oci:logging` |
| `oracle` | `oci_logging` | `oci_logging://OCI_Audit
vehicle-usage-dev` | `ops_non_inf_ocl_m` | `oracle:oci:logging` | `api:oracle:oci:logging` |
| `oracle` | `oci_logging` | `oci_logging://OCI_Audit
vehicle-usage-dev-arch` | `ops_non_inf_ocl_m` | `oracle:oci:logging` | `api:oracle:oci:logging` |
| `oracle` | `oci_logging` | `oci_logging://OCI_Audit
vehicle-usage-dev-error` | `ops_non_inf_ocl_m` | `oracle:oci:logging` | `api:oracle:oci:logging` |
| `oracle` | `oci_logging` | `oci_logging://OCI_Audit
vehicle-usage-uat` | `ops_non_inf_ocl_m` | `oracle:oci:logging` | `api:oracle:oci:logging` |
| `oracle` | `recovery` | `oci_logging://OCI_Audit` | `ops_non_inf_bad_s` | `oracle:unclassified` | `api:oracle:unclassified` |
| `oracle` | `recovery` | `oci_logging://OCI_Audit
svc_oci_network_diagram` | `ops_non_inf_bad_s` | `oracle:unclassified` | `api:oracle:unclassified` |
| `oracle` | `work` | `oci_logging://OCI_Audit` | `ops_non_inf_bad_s` | `oracle:unclassified` | `api:oracle:unclassified` |
| `osnix` | `linux_messages_syslog` | `udp:5005` | `ops_non_inf_lin_m` | `linux:system:messages` | `file:linux:messages` |
| `osnix` | `linux_secure` | `udp:5006` | `res_non_sec_lin_l` | `linux:system:secure` | `file:linux:secure` |
| `osnix` | `syslog` | `/data/logs/host-002fc3c7.example.invalid/adclient.log` | `ops_non_inf_lin_m` | `linux:system:syslog` | `net:linux:syslog` |
| `osnix` | `syslog` | `/data/logs/host-002fc3c7.example.invalid/adinfo.log` | `ops_non_inf_lin_m` | `linux:system:syslog` | `net:linux:syslog` |
| `osnix` | `syslog` | `/data/logs/host-002fc3c7.example.invalid/ansible-command.log` | `ops_non_inf_lin_m` | `linux:system:syslog` | `net:linux:syslog` |
| `osnix` | `syslog` | `/data/logs/host-002fc3c7.example.invalid/kernel.log` | `ops_non_inf_lin_m` | `linux:system:syslog` | `net:linux:syslog` |
| `osnix` | `syslog` | `/data/logs/host-002fc3c7.example.invalid/linux_smartcard_certgp.pl.log` | `ops_non_inf_lin_m` | `linux:system:syslog` | `net:linux:syslog` |
| `osnix` | `syslog` | `/data/logs/host-002fc3c7.example.invalid/report_installed_packages.pl.log` | `ops_non_inf_lin_m` | `linux:system:syslog` | `net:linux:syslog` |
| `osnix` | `syslog` | `/data/logs/host-002fc3c7.example.invalid/rpcbind.log` | `ops_non_inf_lin_m` | `linux:system:syslog` | `net:linux:syslog` |
| `osnix` | `syslog` | `/data/logs/host-002fc3c7.example.invalid/rsyslogd-2177.log` | `ops_non_inf_lin_m` | `linux:system:syslog` | `net:linux:syslog` |
| `osnix` | `syslog` | `/data/logs/host-002fc3c7.example.invalid/runmappers.log` | `ops_non_inf_lin_m` | `linux:system:syslog` | `net:linux:syslog` |
| `osnix` | `syslog` | `/data/logs/host-002fc3c7.example.invalid/snmpd.log` | `ops_non_inf_lin_m` | `linux:system:syslog` | `net:linux:syslog` |
| `osnix` | `syslog` | `/data/logs/host-002fc3c7.example.invalid/sshd.log` | `ops_non_inf_lin_m` | `linux:system:syslog` | `net:linux:syslog` |
| `osnix` | `syslog` | `/data/logs/host-002fc3c7.example.invalid/sudo.log` | `ops_non_inf_lin_m` | `linux:system:syslog` | `net:linux:syslog` |
| `osnix` | `syslog` | `/data/logs/host-0dc766bf.example.invalid/adclient.log` | `ops_non_inf_lin_m` | `linux:system:syslog` | `net:linux:syslog` |
| `osnix` | `syslog` | `/data/logs/host-0dc766bf.example.invalid/adinfo.log` | `ops_non_inf_lin_m` | `linux:system:syslog` | `net:linux:syslog` |
| `osnix` | `syslog` | `/data/logs/host-0dc766bf.example.invalid/ansible-command.log` | `ops_non_inf_lin_m` | `linux:system:syslog` | `net:linux:syslog` |
| `osnix` | `syslog` | `/data/logs/host-0dc766bf.example.invalid/report_installed_packages.pl.log` | `ops_non_inf_lin_m` | `linux:system:syslog` | `net:linux:syslog` |
| `osnix` | `syslog` | `/data/logs/host-0dc766bf.example.invalid/runmappers.log` | `ops_non_inf_lin_m` | `linux:system:syslog` | `net:linux:syslog` |
| `osnix` | `syslog` | `/data/logs/host-0dc766bf.example.invalid/sshd.log` | `ops_non_inf_lin_m` | `linux:system:syslog` | `net:linux:syslog` |
| `osnix` | `syslog` | `/data/logs/host-0dc766bf.example.invalid/sudo.log` | `ops_non_inf_lin_m` | `linux:system:syslog` | `net:linux:syslog` |
| `osnix` | `syslog` | `/data/logs/host-167ca8b5.example.invalid/adclient.log` | `ops_non_inf_lin_m` | `linux:system:syslog` | `net:linux:syslog` |
| `osnix` | `syslog` | `/data/logs/host-167ca8b5.example.invalid/adinfo.log` | `ops_non_inf_lin_m` | `linux:system:syslog` | `net:linux:syslog` |
| `osnix` | `syslog` | `/data/logs/host-167ca8b5.example.invalid/report_installed_packages.pl.log` | `ops_non_inf_lin_m` | `linux:system:syslog` | `net:linux:syslog` |
| `osnix` | `syslog` | `/data/logs/host-1ddd751e.example.invalid/#000#000#000#026.log` | `ops_non_inf_lin_m` | `linux:system:syslog` | `net:linux:syslog` |
| `osnix` | `syslog` | `/data/logs/host-1ddd751e.example.invalid/#000#000#000@#002#003.log` | `ops_non_inf_lin_m` | `linux:system:syslog` | `net:linux:syslog` |
| `osnix` | `syslog` | `/data/logs/host-1ddd751e.example.invalid/#000#000#007#000#000#000;#000#000#000#000#000#000#000#000#000#000#000#000#000#000#000#000#000#000#000#000#000#000#000#000#000#000#000.log` | `ops_non_inf_lin_m` | `linux:system:syslog` | `net:linux:syslog` |
| `osnix` | `syslog` | `/data/logs/host-1ddd751e.example.invalid/#003#000#000#023#016.log` | `ops_non_inf_lin_m` | `linux:system:syslog` | `net:linux:syslog` |
| `osnix` | `syslog` | `/data/logs/host-1ddd751e.example.invalid/#003#001.log` | `ops_non_inf_lin_m` | `linux:system:syslog` | `net:linux:syslog` |
| `osnix` | `syslog` | `/data/logs/host-1ddd751e.example.invalid/#015.log` | `ops_non_inf_lin_m` | `linux:system:syslog` | `net:linux:syslog` |
| `osnix` | `syslog` | `/data/logs/host-1ddd751e.example.invalid/#035.log` | `ops_non_inf_lin_m` | `linux:system:syslog` | `net:linux:syslog` |
| `osnix` | `syslog` | `/data/logs/host-1ddd751e.example.invalid/${jndi.log` | `ops_non_inf_lin_m` | `linux:system:syslog` | `net:linux:syslog` |
| `osnix` | `syslog` | `/data/logs/host-1ddd751e.example.invalid/Accept-Charset.log` | `ops_non_inf_lin_m` | `linux:system:syslog` | `net:linux:syslog` |
| `osnix` | `syslog` | `/data/logs/host-1ddd751e.example.invalid/Accept-Encoding.log` | `ops_non_inf_lin_m` | `linux:system:syslog` | `net:linux:syslog` |
| `osnix` | `syslog` | `/data/logs/host-1ddd751e.example.invalid/Accept-Language.log` | `ops_non_inf_lin_m` | `linux:system:syslog` | `net:linux:syslog` |
| `osnix` | `syslog` | `/data/logs/host-1ddd751e.example.invalid/Accept.log` | `ops_non_inf_lin_m` | `linux:system:syslog` | `net:linux:syslog` |
| `osnix` | `syslog` | `/data/logs/host-1ddd751e.example.invalid/Client-ATV-Sharing-Version.log` | `ops_non_inf_lin_m` | `linux:system:syslog` | `net:linux:syslog` |
| `osnix` | `syslog` | `/data/logs/host-1ddd751e.example.invalid/Client-DAAP-Version.log` | `ops_non_inf_lin_m` | `linux:system:syslog` | `net:linux:syslog` |
| `osnix` | `syslog` | `/data/logs/host-1ddd751e.example.invalid/Client-iTunes-Sharing-Version.log` | `ops_non_inf_lin_m` | `linux:system:syslog` | `net:linux:syslog` |
| `osnix` | `syslog` | `/data/logs/host-1ddd751e.example.invalid/Connection.log` | `ops_non_inf_lin_m` | `linux:system:syslog` | `net:linux:syslog` |
| `osnix` | `syslog` | `/data/logs/host-1ddd751e.example.invalid/HELP#015.log` | `ops_non_inf_lin_m` | `linux:system:syslog` | `net:linux:syslog` |
| `osnix` | `syslog` | `/data/logs/host-1ddd751e.example.invalid/Host.log` | `ops_non_inf_lin_m` | `linux:system:syslog` | `net:linux:syslog` |
| `osnix` | `syslog` | `/data/logs/host-1ddd751e.example.invalid/I#000#000#000f#000#000.log` | `ops_non_inf_lin_m` | `linux:system:syslog` | `net:linux:syslog` |
| `osnix` | `syslog` | `/data/logs/host-1ddd751e.example.invalid/Pragma.log` | `ops_non_inf_lin_m` | `linux:system:syslog` | `net:linux:syslog` |
| `osnix` | `syslog` | `/data/logs/host-1ddd751e.example.invalid/User-Agent.log` | `ops_non_inf_lin_m` | `linux:system:syslog` | `net:linux:syslog` |
| `osnix` | `syslog` | `/data/logs/host-1ddd751e.example.invalid/Viewer-Only-Client.log` | `ops_non_inf_lin_m` | `linux:system:syslog` | `net:linux:syslog` |
| `osnix` | `syslog` | `/data/logs/host-1ddd751e.example.invalid/login?hsgid={guid}&hasFP=1.log` | `ops_non_inf_lin_m` | `linux:system:syslog` | `net:linux:syslog` |
| `osnix` | `syslog` | `/data/logs/host-1ddd751e.example.invalid/rU#000#000#012#035.log` | `ops_non_inf_lin_m` | `linux:system:syslog` | `net:linux:syslog` |
| `osnix` | `syslog` | `/data/logs/host-1ddd751e.example.invalid/root#000root#000id.log` | `ops_non_inf_lin_m` | `linux:system:syslog` | `net:linux:syslog` |
| `osnix` | `syslog` | `/data/logs/host-3b977d04.example.invalid/adclient.log` | `ops_non_inf_lin_m` | `linux:system:syslog` | `net:linux:syslog` |
| `osnix` | `syslog` | `/data/logs/host-3b977d04.example.invalid/adinfo.log` | `ops_non_inf_lin_m` | `linux:system:syslog` | `net:linux:syslog` |
| `osnix` | `syslog` | `/data/logs/host-3b977d04.example.invalid/dad.log` | `ops_non_inf_lin_m` | `linux:system:syslog` | `net:linux:syslog` |
| `osnix` | `syslog` | `/data/logs/host-3b977d04.example.invalid/report_installed_packages.pl.log` | `ops_non_inf_lin_m` | `linux:system:syslog` | `net:linux:syslog` |
| `osnix` | `syslog` | `/data/logs/host-3b977d04.example.invalid/sendmail.log` | `ops_non_inf_lin_m` | `linux:system:syslog` | `net:linux:syslog` |
| `osnix` | `syslog` | `/data/logs/host-3b977d04.example.invalid/sshd.log` | `ops_non_inf_lin_m` | `linux:system:syslog` | `net:linux:syslog` |
| `osnix` | `syslog` | `/data/logs/host-3f7bc865.example.invalid/adclient.log` | `ops_non_inf_lin_m` | `linux:system:syslog` | `net:linux:syslog` |
| `osnix` | `syslog` | `/data/logs/host-3f7bc865.example.invalid/adinfo.log` | `ops_non_inf_lin_m` | `linux:system:syslog` | `net:linux:syslog` |
| `osnix` | `syslog` | `/data/logs/host-3f7bc865.example.invalid/report_installed_packages.pl.log` | `ops_non_inf_lin_m` | `linux:system:syslog` | `net:linux:syslog` |
| `osnix` | `syslog` | `/data/logs/host-3f7bc865.example.invalid/sendmail.log` | `ops_non_inf_lin_m` | `linux:system:syslog` | `net:linux:syslog` |
| `osnix` | `syslog` | `/data/logs/host-419d0f1b.example.invalid/adclient.log` | `ops_non_inf_lin_m` | `linux:system:syslog` | `net:linux:syslog` |
| `osnix` | `syslog` | `/data/logs/host-419d0f1b.example.invalid/adinfo.log` | `ops_non_inf_lin_m` | `linux:system:syslog` | `net:linux:syslog` |
| `osnix` | `syslog` | `/data/logs/host-419d0f1b.example.invalid/report_installed_packages.pl.log` | `ops_non_inf_lin_m` | `linux:system:syslog` | `net:linux:syslog` |
| `osnix` | `syslog` | `/data/logs/host-4ab2d87d.example.invalid/adclient.log` | `ops_non_inf_lin_m` | `linux:system:syslog` | `net:linux:syslog` |
| `osnix` | `syslog` | `/data/logs/host-4ab2d87d.example.invalid/adinfo.log` | `ops_non_inf_lin_m` | `linux:system:syslog` | `net:linux:syslog` |
| `osnix` | `syslog` | `/data/logs/host-4ab2d87d.example.invalid/report_installed_packages.pl.log` | `ops_non_inf_lin_m` | `linux:system:syslog` | `net:linux:syslog` |
| `osnix` | `syslog` | `/data/logs/host-4ab2d87d.example.invalid/sendmail.log` | `ops_non_inf_lin_m` | `linux:system:syslog` | `net:linux:syslog` |
| `osnix` | `syslog` | `/data/logs/host-6c567d3b.example.invalid/adclient.log` | `ops_non_inf_lin_m` | `linux:system:syslog` | `net:linux:syslog` |
| `osnix` | `syslog` | `/data/logs/host-6c567d3b.example.invalid/adinfo.log` | `ops_non_inf_lin_m` | `linux:system:syslog` | `net:linux:syslog` |
| `osnix` | `syslog` | `/data/logs/host-6c567d3b.example.invalid/dad.log` | `ops_non_inf_lin_m` | `linux:system:syslog` | `net:linux:syslog` |
| `osnix` | `syslog` | `/data/logs/host-6c567d3b.example.invalid/inetd.log` | `ops_non_inf_lin_m` | `linux:system:syslog` | `net:linux:syslog` |
| `osnix` | `syslog` | `/data/logs/host-6c567d3b.example.invalid/mountd.log` | `ops_non_inf_lin_m` | `linux:system:syslog` | `net:linux:syslog` |
| `osnix` | `syslog` | `/data/logs/host-6c567d3b.example.invalid/ntpd.log` | `ops_non_inf_lin_m` | `linux:system:syslog` | `net:linux:syslog` |
| `osnix` | `syslog` | `/data/logs/host-6c567d3b.example.invalid/report_installed_packages.pl.log` | `ops_non_inf_lin_m` | `linux:system:syslog` | `net:linux:syslog` |
| `osnix` | `syslog` | `/data/logs/host-6c567d3b.example.invalid/sm-mta.log` | `ops_non_inf_lin_m` | `linux:system:syslog` | `net:linux:syslog` |
| `osnix` | `syslog` | `/data/logs/host-6c567d3b.example.invalid/sshd.log` | `ops_non_inf_lin_m` | `linux:system:syslog` | `net:linux:syslog` |
| `osnix` | `syslog` | `/data/logs/host-6c567d3b.example.invalid/tftpd.log` | `ops_non_inf_lin_m` | `linux:system:syslog` | `net:linux:syslog` |
| `osnix` | `syslog` | `/data/logs/host-8cba8e75.example.invalid/adclient.log` | `ops_non_inf_lin_m` | `linux:system:syslog` | `net:linux:syslog` |
| `osnix` | `syslog` | `/data/logs/host-8cba8e75.example.invalid/adinfo.log` | `ops_non_inf_lin_m` | `linux:system:syslog` | `net:linux:syslog` |
| `osnix` | `syslog` | `/data/logs/host-8cba8e75.example.invalid/ansible-command.log` | `ops_non_inf_lin_m` | `linux:system:syslog` | `net:linux:syslog` |
| `osnix` | `syslog` | `/data/logs/host-8cba8e75.example.invalid/ntpd_intres.log` | `ops_non_inf_lin_m` | `linux:system:syslog` | `net:linux:syslog` |
| `osnix` | `syslog` | `/data/logs/host-8cba8e75.example.invalid/report_installed_packages.pl.log` | `ops_non_inf_lin_m` | `linux:system:syslog` | `net:linux:syslog` |
| `osnix` | `syslog` | `/data/logs/host-8cba8e75.example.invalid/runmappers.log` | `ops_non_inf_lin_m` | `linux:system:syslog` | `net:linux:syslog` |
| `osnix` | `syslog` | `/data/logs/host-8cba8e75.example.invalid/sshd.log` | `ops_non_inf_lin_m` | `linux:system:syslog` | `net:linux:syslog` |
| `osnix` | `syslog` | `/data/logs/host-8cba8e75.example.invalid/sudo.log` | `ops_non_inf_lin_m` | `linux:system:syslog` | `net:linux:syslog` |
| `osnix` | `syslog` | `/data/logs/host-913bf97a.example.invalid/.log` | `ops_non_inf_lin_m` | `linux:system:syslog` | `net:linux:syslog` |
| `osnix` | `syslog` | `/data/logs/host-913bf97a.example.invalid/adclient.log` | `ops_non_inf_lin_m` | `linux:system:syslog` | `net:linux:syslog` |
| `osnix` | `syslog` | `/data/logs/host-913bf97a.example.invalid/adinfo.log` | `ops_non_inf_lin_m` | `linux:system:syslog` | `net:linux:syslog` |
| `osnix` | `syslog` | `/data/logs/host-913bf97a.example.invalid/dad.log` | `ops_non_inf_lin_m` | `linux:system:syslog` | `net:linux:syslog` |
| `osnix` | `syslog` | `/data/logs/host-913bf97a.example.invalid/mountd.log` | `ops_non_inf_lin_m` | `linux:system:syslog` | `net:linux:syslog` |
| `osnix` | `syslog` | `/data/logs/host-913bf97a.example.invalid/report_installed_packages.pl.log` | `ops_non_inf_lin_m` | `linux:system:syslog` | `net:linux:syslog` |
| `osnix` | `syslog` | `/data/logs/host-913bf97a.example.invalid/sm-mta.log` | `ops_non_inf_lin_m` | `linux:system:syslog` | `net:linux:syslog` |
| `osnix` | `syslog` | `/data/logs/host-913bf97a.example.invalid/sshd.log` | `ops_non_inf_lin_m` | `linux:system:syslog` | `net:linux:syslog` |
| `osnix` | `syslog` | `/data/logs/host-913bf97a.example.invalid/syslog.log` | `ops_non_inf_lin_m` | `linux:system:syslog` | `net:linux:syslog` |
| `osnix` | `syslog` | `/data/logs/host-913bf97a.example.invalid/vmunix.log` | `ops_non_inf_lin_m` | `linux:system:syslog` | `net:linux:syslog` |
| `osnix` | `syslog` | `/data/logs/host-9ba{digits}.example.invalid/adclient.log` | `ops_non_inf_lin_m` | `linux:system:syslog` | `net:linux:syslog` |
| `osnix` | `syslog` | `/data/logs/host-9ba{digits}.example.invalid/adinfo.log` | `ops_non_inf_lin_m` | `linux:system:syslog` | `net:linux:syslog` |
| `osnix` | `syslog` | `/data/logs/host-9ba{digits}.example.invalid/dad.log` | `ops_non_inf_lin_m` | `linux:system:syslog` | `net:linux:syslog` |
| `osnix` | `syslog` | `/data/logs/host-9ba{digits}.example.invalid/inetd.log` | `ops_non_inf_lin_m` | `linux:system:syslog` | `net:linux:syslog` |
| `osnix` | `syslog` | `/data/logs/host-9ba{digits}.example.invalid/mountd.log` | `ops_non_inf_lin_m` | `linux:system:syslog` | `net:linux:syslog` |
| `osnix` | `syslog` | `/data/logs/host-9ba{digits}.example.invalid/report_installed_packages.pl.log` | `ops_non_inf_lin_m` | `linux:system:syslog` | `net:linux:syslog` |
| `osnix` | `syslog` | `/data/logs/host-9ba{digits}.example.invalid/runmappers.log` | `ops_non_inf_lin_m` | `linux:system:syslog` | `net:linux:syslog` |
| `osnix` | `syslog` | `/data/logs/host-9ba{digits}.example.invalid/sm-mta.log` | `ops_non_inf_lin_m` | `linux:system:syslog` | `net:linux:syslog` |
| `osnix` | `syslog` | `/data/logs/host-9ba{digits}.example.invalid/sshd.log` | `ops_non_inf_lin_m` | `linux:system:syslog` | `net:linux:syslog` |
| `osnix` | `syslog` | `/data/logs/host-9ba{digits}.example.invalid/tftpd.log` | `ops_non_inf_lin_m` | `linux:system:syslog` | `net:linux:syslog` |
| `osnix` | `syslog` | `/data/logs/host-9fe650a0.example.invalid/adclient.log` | `ops_non_inf_lin_m` | `linux:system:syslog` | `net:linux:syslog` |
| `osnix` | `syslog` | `/data/logs/host-9fe650a0.example.invalid/adinfo.log` | `ops_non_inf_lin_m` | `linux:system:syslog` | `net:linux:syslog` |
| `osnix` | `syslog` | `/data/logs/host-9fe650a0.example.invalid/dad.log` | `ops_non_inf_lin_m` | `linux:system:syslog` | `net:linux:syslog` |
| `osnix` | `syslog` | `/data/logs/host-9fe650a0.example.invalid/inetd.log` | `ops_non_inf_lin_m` | `linux:system:syslog` | `net:linux:syslog` |
| `osnix` | `syslog` | `/data/logs/host-9fe650a0.example.invalid/mountd.log` | `ops_non_inf_lin_m` | `linux:system:syslog` | `net:linux:syslog` |
| `osnix` | `syslog` | `/data/logs/host-9fe650a0.example.invalid/report_installed_packages.pl.log` | `ops_non_inf_lin_m` | `linux:system:syslog` | `net:linux:syslog` |
| `osnix` | `syslog` | `/data/logs/host-9fe650a0.example.invalid/runmappers.log` | `ops_non_inf_lin_m` | `linux:system:syslog` | `net:linux:syslog` |
| `osnix` | `syslog` | `/data/logs/host-9fe650a0.example.invalid/sm-mta.log` | `ops_non_inf_lin_m` | `linux:system:syslog` | `net:linux:syslog` |
| `osnix` | `syslog` | `/data/logs/host-9fe650a0.example.invalid/sshd.log` | `ops_non_inf_lin_m` | `linux:system:syslog` | `net:linux:syslog` |
| `osnix` | `syslog` | `/data/logs/host-9fe650a0.example.invalid/tftpd.log` | `ops_non_inf_lin_m` | `linux:system:syslog` | `net:linux:syslog` |
| `osnix` | `syslog` | `/data/logs/host-aa{digits}.example.invalid/adclient.log` | `ops_non_inf_lin_m` | `linux:system:syslog` | `net:linux:syslog` |
| `osnix` | `syslog` | `/data/logs/host-aa{digits}.example.invalid/adinfo.log` | `ops_non_inf_lin_m` | `linux:system:syslog` | `net:linux:syslog` |
| `osnix` | `syslog` | `/data/logs/host-aa{digits}.example.invalid/dad.log` | `ops_non_inf_lin_m` | `linux:system:syslog` | `net:linux:syslog` |
| `osnix` | `syslog` | `/data/logs/host-aa{digits}.example.invalid/dzdo.log` | `ops_non_inf_lin_m` | `linux:system:syslog` | `net:linux:syslog` |
| `osnix` | `syslog` | `/data/logs/host-aa{digits}.example.invalid/report_installed_packages.pl.log` | `ops_non_inf_lin_m` | `linux:system:syslog` | `net:linux:syslog` |
| `osnix` | `syslog` | `/data/logs/host-ab{digits}.example.invalid/adclient.log` | `ops_non_inf_lin_m` | `linux:system:syslog` | `net:linux:syslog` |
| `osnix` | `syslog` | `/data/logs/host-ab{digits}.example.invalid/adinfo.log` | `ops_non_inf_lin_m` | `linux:system:syslog` | `net:linux:syslog` |
| `osnix` | `syslog` | `/data/logs/host-ab{digits}.example.invalid/report_installed_packages.pl.log` | `ops_non_inf_lin_m` | `linux:system:syslog` | `net:linux:syslog` |
| `osnix` | `syslog` | `/data/logs/host-a{digits}b.example.invalid/adclient.log` | `ops_non_inf_lin_m` | `linux:system:syslog` | `net:linux:syslog` |
| `osnix` | `syslog` | `/data/logs/host-a{digits}b.example.invalid/adinfo.log` | `ops_non_inf_lin_m` | `linux:system:syslog` | `net:linux:syslog` |
| `osnix` | `syslog` | `/data/logs/host-a{digits}b.example.invalid/dad.log` | `ops_non_inf_lin_m` | `linux:system:syslog` | `net:linux:syslog` |
| `osnix` | `syslog` | `/data/logs/host-a{digits}b.example.invalid/inetd.log` | `ops_non_inf_lin_m` | `linux:system:syslog` | `net:linux:syslog` |
| `osnix` | `syslog` | `/data/logs/host-a{digits}b.example.invalid/mountd.log` | `ops_non_inf_lin_m` | `linux:system:syslog` | `net:linux:syslog` |
| `osnix` | `syslog` | `/data/logs/host-a{digits}b.example.invalid/report_installed_packages.pl.log` | `ops_non_inf_lin_m` | `linux:system:syslog` | `net:linux:syslog` |
| `osnix` | `syslog` | `/data/logs/host-a{digits}b.example.invalid/runmappers.log` | `ops_non_inf_lin_m` | `linux:system:syslog` | `net:linux:syslog` |
| `osnix` | `syslog` | `/data/logs/host-a{digits}b.example.invalid/sm-mta.log` | `ops_non_inf_lin_m` | `linux:system:syslog` | `net:linux:syslog` |
| `osnix` | `syslog` | `/data/logs/host-a{digits}b.example.invalid/sshd.log` | `ops_non_inf_lin_m` | `linux:system:syslog` | `net:linux:syslog` |
| `osnix` | `syslog` | `/data/logs/host-a{digits}b.example.invalid/tftpd.log` | `ops_non_inf_lin_m` | `linux:system:syslog` | `net:linux:syslog` |
| `osnix` | `syslog` | `/data/logs/host-caad785f.example.invalid/adclient.log` | `ops_non_inf_lin_m` | `linux:system:syslog` | `net:linux:syslog` |
| `osnix` | `syslog` | `/data/logs/host-caad785f.example.invalid/adinfo.log` | `ops_non_inf_lin_m` | `linux:system:syslog` | `net:linux:syslog` |
| `osnix` | `syslog` | `/data/logs/host-caad785f.example.invalid/ansible-command.log` | `ops_non_inf_lin_m` | `linux:system:syslog` | `net:linux:syslog` |
| `osnix` | `syslog` | `/data/logs/host-caad785f.example.invalid/kernel.log` | `ops_non_inf_lin_m` | `linux:system:syslog` | `net:linux:syslog` |
| `osnix` | `syslog` | `/data/logs/host-caad785f.example.invalid/report_installed_packages.pl.log` | `ops_non_inf_lin_m` | `linux:system:syslog` | `net:linux:syslog` |
| `osnix` | `syslog` | `/data/logs/host-caad785f.example.invalid/rpcbind.log` | `ops_non_inf_lin_m` | `linux:system:syslog` | `net:linux:syslog` |
| `osnix` | `syslog` | `/data/logs/host-caad785f.example.invalid/rsyslogd-2177.log` | `ops_non_inf_lin_m` | `linux:system:syslog` | `net:linux:syslog` |
| `osnix` | `syslog` | `/data/logs/host-caad785f.example.invalid/runmappers.log` | `ops_non_inf_lin_m` | `linux:system:syslog` | `net:linux:syslog` |
| `osnix` | `syslog` | `/data/logs/host-caad785f.example.invalid/snmpd.log` | `ops_non_inf_lin_m` | `linux:system:syslog` | `net:linux:syslog` |
| `osnix` | `syslog` | `/data/logs/host-caad785f.example.invalid/sshd.log` | `ops_non_inf_lin_m` | `linux:system:syslog` | `net:linux:syslog` |
| `osnix` | `syslog` | `/data/logs/host-caad785f.example.invalid/sudo.log` | `ops_non_inf_lin_m` | `linux:system:syslog` | `net:linux:syslog` |
| `osnix` | `syslog` | `/data/logs/host-da806b6a.example.invalid/adclient.log` | `ops_non_inf_lin_m` | `linux:system:syslog` | `net:linux:syslog` |
| `osnix` | `syslog` | `/data/logs/host-da806b6a.example.invalid/adinfo.log` | `ops_non_inf_lin_m` | `linux:system:syslog` | `net:linux:syslog` |
| `osnix` | `syslog` | `/data/logs/host-da806b6a.example.invalid/ansible-command.log` | `ops_non_inf_lin_m` | `linux:system:syslog` | `net:linux:syslog` |
| `osnix` | `syslog` | `/data/logs/host-da806b6a.example.invalid/kernel.log` | `ops_non_inf_lin_m` | `linux:system:syslog` | `net:linux:syslog` |
| `osnix` | `syslog` | `/data/logs/host-da806b6a.example.invalid/ntpd_intres.log` | `ops_non_inf_lin_m` | `linux:system:syslog` | `net:linux:syslog` |
| `osnix` | `syslog` | `/data/logs/host-da806b6a.example.invalid/report_installed_packages.pl.log` | `ops_non_inf_lin_m` | `linux:system:syslog` | `net:linux:syslog` |
| `osnix` | `syslog` | `/data/logs/host-da806b6a.example.invalid/rpcbind.log` | `ops_non_inf_lin_m` | `linux:system:syslog` | `net:linux:syslog` |
| `osnix` | `syslog` | `/data/logs/host-da806b6a.example.invalid/rsyslogd-2177.log` | `ops_non_inf_lin_m` | `linux:system:syslog` | `net:linux:syslog` |
| `osnix` | `syslog` | `/data/logs/host-da806b6a.example.invalid/runmappers.log` | `ops_non_inf_lin_m` | `linux:system:syslog` | `net:linux:syslog` |
| `osnix` | `syslog` | `/data/logs/host-da806b6a.example.invalid/snmpd.log` | `ops_non_inf_lin_m` | `linux:system:syslog` | `net:linux:syslog` |
| `osnix` | `syslog` | `/data/logs/host-da806b6a.example.invalid/sshd.log` | `ops_non_inf_lin_m` | `linux:system:syslog` | `net:linux:syslog` |
| `osnix` | `syslog` | `/data/logs/host-da806b6a.example.invalid/sudo.log` | `ops_non_inf_lin_m` | `linux:system:syslog` | `net:linux:syslog` |
| `osnix` | `syslog` | `/data/logs/host-dc9c1805.example.invalid/adclient.log` | `ops_non_inf_lin_m` | `linux:system:syslog` | `net:linux:syslog` |
| `osnix` | `syslog` | `/data/logs/host-dc9c1805.example.invalid/adinfo.log` | `ops_non_inf_lin_m` | `linux:system:syslog` | `net:linux:syslog` |
| `osnix` | `syslog` | `/data/logs/host-dc9c1805.example.invalid/ansible-command.log` | `ops_non_inf_lin_m` | `linux:system:syslog` | `net:linux:syslog` |
| `osnix` | `syslog` | `/data/logs/host-dc9c1805.example.invalid/kernel.log` | `ops_non_inf_lin_m` | `linux:system:syslog` | `net:linux:syslog` |
| `osnix` | `syslog` | `/data/logs/host-dc9c1805.example.invalid/report_installed_packages.pl.log` | `ops_non_inf_lin_m` | `linux:system:syslog` | `net:linux:syslog` |
| `osnix` | `syslog` | `/data/logs/host-dc9c1805.example.invalid/rpcbind.log` | `ops_non_inf_lin_m` | `linux:system:syslog` | `net:linux:syslog` |
| `osnix` | `syslog` | `/data/logs/host-dc9c1805.example.invalid/rsyslogd-2177.log` | `ops_non_inf_lin_m` | `linux:system:syslog` | `net:linux:syslog` |
| `osnix` | `syslog` | `/data/logs/host-dc9c1805.example.invalid/runmappers.log` | `ops_non_inf_lin_m` | `linux:system:syslog` | `net:linux:syslog` |
| `osnix` | `syslog` | `/data/logs/host-dc9c1805.example.invalid/setroubleshoot.log` | `ops_non_inf_lin_m` | `linux:system:syslog` | `net:linux:syslog` |
| `osnix` | `syslog` | `/data/logs/host-dc9c1805.example.invalid/snmpd.log` | `ops_non_inf_lin_m` | `linux:system:syslog` | `net:linux:syslog` |
| `osnix` | `syslog` | `/data/logs/host-dc9c1805.example.invalid/sshd.log` | `ops_non_inf_lin_m` | `linux:system:syslog` | `net:linux:syslog` |
| `osnix` | `syslog` | `/data/logs/host-dc9c1805.example.invalid/sudo.log` | `ops_non_inf_lin_m` | `linux:system:syslog` | `net:linux:syslog` |
| `osnix` | `syslog` | `/data/logs/host-e{digits}.example.invalid/.log` | `ops_non_inf_lin_m` | `linux:system:syslog` | `net:linux:syslog` |
| `osnix` | `syslog` | `/data/logs/host-e{digits}.example.invalid/adclient.log` | `ops_non_inf_lin_m` | `linux:system:syslog` | `net:linux:syslog` |
| `osnix` | `syslog` | `/data/logs/host-e{digits}.example.invalid/adinfo.log` | `ops_non_inf_lin_m` | `linux:system:syslog` | `net:linux:syslog` |
| `osnix` | `syslog` | `/data/logs/host-e{digits}.example.invalid/dad.log` | `ops_non_inf_lin_m` | `linux:system:syslog` | `net:linux:syslog` |
| `osnix` | `syslog` | `/data/logs/host-e{digits}.example.invalid/inetd.log` | `ops_non_inf_lin_m` | `linux:system:syslog` | `net:linux:syslog` |
| `osnix` | `syslog` | `/data/logs/host-e{digits}.example.invalid/mountd.log` | `ops_non_inf_lin_m` | `linux:system:syslog` | `net:linux:syslog` |
| `osnix` | `syslog` | `/data/logs/host-e{digits}.example.invalid/report_installed_packages.pl.log` | `ops_non_inf_lin_m` | `linux:system:syslog` | `net:linux:syslog` |
| `osnix` | `syslog` | `/data/logs/host-e{digits}.example.invalid/runmappers.log` | `ops_non_inf_lin_m` | `linux:system:syslog` | `net:linux:syslog` |
| `osnix` | `syslog` | `/data/logs/host-e{digits}.example.invalid/sm-mta.log` | `ops_non_inf_lin_m` | `linux:system:syslog` | `net:linux:syslog` |
| `osnix` | `syslog` | `/data/logs/host-e{digits}.example.invalid/sshd.log` | `ops_non_inf_lin_m` | `linux:system:syslog` | `net:linux:syslog` |
| `osnix` | `syslog` | `/data/logs/host-e{digits}.example.invalid/tftpd.log` | `ops_non_inf_lin_m` | `linux:system:syslog` | `net:linux:syslog` |
| `osnix` | `syslog` | `/data/logs/host-{digits}c72.example.invalid/.log` | `ops_non_inf_lin_m` | `linux:system:syslog` | `net:linux:syslog` |
| `osnix` | `syslog` | `/data/logs/host-{digits}c72.example.invalid/adclient.log` | `ops_non_inf_lin_m` | `linux:system:syslog` | `net:linux:syslog` |
| `osnix` | `syslog` | `/data/logs/host-{digits}c72.example.invalid/adinfo.log` | `ops_non_inf_lin_m` | `linux:system:syslog` | `net:linux:syslog` |
| `osnix` | `syslog` | `/data/logs/host-{digits}c72.example.invalid/dad.log` | `ops_non_inf_lin_m` | `linux:system:syslog` | `net:linux:syslog` |
| `osnix` | `syslog` | `/data/logs/host-{digits}c72.example.invalid/mountd.log` | `ops_non_inf_lin_m` | `linux:system:syslog` | `net:linux:syslog` |
| `osnix` | `syslog` | `/data/logs/host-{digits}c72.example.invalid/report_installed_packages.pl.log` | `ops_non_inf_lin_m` | `linux:system:syslog` | `net:linux:syslog` |
| `osnix` | `syslog` | `/data/logs/host-{digits}c72.example.invalid/sm-mta.log` | `ops_non_inf_lin_m` | `linux:system:syslog` | `net:linux:syslog` |
| `osnix` | `syslog` | `/data/logs/host-{digits}c72.example.invalid/sshd.log` | `ops_non_inf_lin_m` | `linux:system:syslog` | `net:linux:syslog` |
| `osnix` | `syslog` | `/data/logs/host-{digits}c72.example.invalid/syslog.log` | `ops_non_inf_lin_m` | `linux:system:syslog` | `net:linux:syslog` |
| `osnix` | `syslog` | `/data/logs/host-{digits}c72.example.invalid/vmunix.log` | `ops_non_inf_lin_m` | `linux:system:syslog` | `net:linux:syslog` |
| `osnix` | `syslog` | `tcp:5055` | `ops_non_inf_lin_m` | `linux:system:syslog` | `net:linux:syslog` |
| `oswin` | `XmlWinEventLog` | `XmlWinEventLog:Application` | `ops_non_inf_win_m` | `microsoft:windows:eventlog:xml` | `win:eventlog:application` |
| `oswin` | `XmlWinEventLog` | `XmlWinEventLog:System` | `ops_non_inf_win_m` | `microsoft:windows:eventlog:xml` | `win:eventlog:system` |
| `oswinsec` | `XmlWinEventLog` | `XmlWinEventLog:Security` | `res_non_sec_win_l` | `microsoft:windows:eventlog:xml` | `win:eventlog:security` |
| `palo_alto` | `pan:correlation` | `udp:5050` | `res_non_sec_fwl_l` | `pan:correlation` | `net:paloalto:pan:correlation` |
| `palo_alto` | `pan:globalprotect` | `udp:5050` | `res_non_sec_fwl_l` | `pan:globalprotect` | `net:paloalto:pan:globalprotect` |
| `palo_alto` | `pan:hipmatch` | `udp:5050` | `res_non_sec_fwl_l` | `pan:hipmatch` | `net:paloalto:pan:hipmatch` |
| `palo_alto` | `pan:system` | `udp:5050` | `res_non_sec_fwl_l` | `pan:system` | `net:paloalto:pan:system` |
| `palo_alto` | `pan:threat` | `udp:5050` | `res_non_sec_fwl_l` | `pan:threat` | `net:paloalto:pan:threat` |
| `palo_alto` | `pan:traffic` | `udp:5050` | `res_non_sec_fwl_l` | `pan:traffic` | `net:paloalto:pan:traffic` |
| `risk` | `stash` | `Access - Brute Force Access Behavior Detected - Rule` | `risk` | `stash` | `es:risk:access_brute_force_access_behavior_detected_rule` |
| `risk` | `stash` | `Access - Concurrent App Accesses - Rule` | `risk` | `stash` | `es:risk:access_concurrent_app_accesses_rule` |
| `risk` | `stash` | `Access - Default Account Usage - Rule` | `risk` | `stash` | `es:risk:access_default_account_usage_rule` |
| `risk` | `stash` | `ESCU - O365 Excessive Authentication Failures Alert - Rule` | `risk` | `stash` | `es:risk:escu_o365_excessive_authentication_failures_alert_rule` |
| `risk` | `stash` | `ESCU - O365 Excessive SSO logon errors - Rule` | `risk` | `stash` | `es:risk:escu_o365_excessive_sso_logon_errors_rule` |
| `risk` | `stash` | `ESCU - O365 External Guest User Invited - Rule` | `risk` | `stash` | `es:risk:escu_o365_external_guest_user_invited_rule` |
| `risk` | `stash` | `ESCU - Windows Create Local Account - Rule` | `risk` | `stash` | `es:risk:escu_windows_create_local_account_rule` |
| `risk` | `stash` | `Endpoint - Anomalous New Processes - Rule` | `risk` | `stash` | `es:risk:endpoint_anomalous_new_processes_rule` |
| `risk` | `stash` | `Identity - High Volume Email Activity with Non-corporate Domains - Rule` | `risk` | `stash` | `es:risk:identity_high_volume_email_activity_with_non-corporate_domains_rule` |
| `risk` | `stash` | `Web - Abnormally High Number of HTTP Method Events By Src - Rule` | `risk` | `stash` | `es:risk:web_abnormally_high_number_of_http_method_events_by_src_rule` |
| `servicenow` | `snow:cmdb_ci_list` | `https://{host}/` | `ent_non_app_itm_m` | `servicenow:cmdb:ci` | `api:servicenow:cmdb:ci` |
| `snare_logs` | `wineventlog` | `WinEventLog` | `ops_non_inf_win_m` | `microsoft:windows:eventlog:snare` | `net:snare:windows:eventlog` |
| `snare_logs` | `wineventlog` | `WinEventLog:Application` | `ops_non_inf_win_m` | `microsoft:windows:eventlog:snare` | `net:snare:windows:eventlog` |
| `snare_logs` | `wineventlog` | `WinEventLog:Security` | `ops_non_inf_win_m` | `microsoft:windows:eventlog:snare` | `net:snare:windows:eventlog` |
| `snare_logs` | `wineventlog` | `WinEventLog:System` | `ops_non_inf_win_m` | `microsoft:windows:eventlog:snare` | `net:snare:windows:eventlog` |
| `snare_logs` | `wineventlog` | `udp:5001` | `ops_non_inf_win_m` | `microsoft:windows:eventlog:snare` | `net:snare:windows:eventlog` |
| `summary` | `stash` | `cmc-thresholds` | `summary` | `stash` | `splunk:summary:cmc-thresholds` |
| `summary` | `stash` | `default_is4s_ssef_hourly_group` | `summary` | `stash` | `splunk:summary:default_is4s_ssef_hourly_group` |
| `summary` | `stash` | `splunk-entitlements` | `summary` | `stash` | `splunk:summary:splunk-entitlements` |
| `summary` | `stash` | `splunk-ingestion` | `summary` | `stash` | `splunk:summary:splunk-ingestion` |
| `summary` | `stash` | `splunk-search-count` | `summary` | `stash` | `splunk:summary:splunk-search-count` |
| `summary` | `stash` | `splunk-storage-detail` | `summary` | `stash` | `splunk:summary:splunk-storage-detail` |
| `summary` | `stash` | `splunk-storage-summary` | `summary` | `stash` | `splunk:summary:splunk-storage-summary` |
| `summary` | `stash` | `splunk-svc` | `summary` | `stash` | `splunk:summary:splunk-svc` |
| `summary` | `stash` | `splunk-svc-consumer` | `summary` | `stash` | `splunk:summary:splunk-svc-consumer` |
| `summary` | `stash` | `splunk_search_breakdown` | `summary` | `stash` | `splunk:summary:splunk_search_breakdown` |
| `summary` | `stash` | `ssef_audit_user_login_tracker` | `summary` | `stash` | `splunk:summary:ssef_audit_user_login_tracker` |
| `summary` | `stash` | `ssef_internal_splunkd_ui_access_tracker` | `summary` | `stash` | `splunk:summary:ssef_internal_splunkd_ui_access_tracker` |
| `summary` | `stash` | `ssef_internal_web_access_tracker` | `summary` | `stash` | `splunk:summary:ssef_internal_web_access_tracker` |
| `summary` | `stash` | `ssef_search_failed_jobs_tracker` | `summary` | `stash` | `splunk:summary:ssef_search_failed_jobs_tracker` |
| `thales_hsm` | `syslog` | `tcp:5022` | `res_pci_sec_hsm_l` | `thales:hsm:syslog` | `net:thales:hsm:syslog` |
| `threat_activity` | `stash` | `threatmatch://dest` | `threat_activity` | `stash` | `es:threat:threatmatch_dest` |
| `threat_activity` | `stash` | `threatmatch://file_hash` | `threat_activity` | `stash` | `es:threat:threatmatch_file_hash` |
| `threat_activity` | `stash` | `threatmatch://src` | `threat_activity` | `stash` | `es:threat:threatmatch_src` |
| `varonis` | `varonis:ta` | `udp:5025` | `res_non_sec_dlp_l` | `varonis:datasecurity:audit` | `api:varonis:datasecurity` |
| `vmware` | `vmw-syslog` | `vmware:esxlog:source::tcp:1514` | `ops_non_inf_vmw_s` | `vmware:esx:syslog` | `net:vmware:esx:syslog` |
| `vmware` | `vmw-syslog` | `vmware:esxlog:source::udp:1514` | `ops_non_inf_vmw_s` | `vmware:esx:syslog` | `net:vmware:esx:syslog` |
| `vmware` | `vmware:esxlog:ConfigStore` | `vmware:esxlog:source::tcp:1514` | `ops_non_inf_vmw_s` | `vmware:esxlog:configstore` | `net:vmware:esx:syslog` |
| `vmware` | `vmware:esxlog:Fdm` | `vmware:esxlog:source::tcp:1514` | `ops_non_inf_vmw_s` | `vmware:esxlog:fdm` | `net:vmware:esx:syslog` |
| `vmware` | `vmware:esxlog:Hostd` | `vmware:esxlog:source::tcp:1514` | `ops_non_inf_vmw_s` | `vmware:esxlog:hostd` | `net:vmware:esx:syslog` |
| `vmware` | `vmware:esxlog:Rhttpproxy` | `vmware:esxlog:source::tcp:1514` | `ops_non_inf_vmw_s` | `vmware:esxlog:rhttpproxy` | `net:vmware:esx:syslog` |
| `vmware` | `vmware:esxlog:Vpxa` | `vmware:esxlog:source::tcp:1514` | `ops_non_inf_vmw_s` | `vmware:esxlog:vpxa` | `net:vmware:esx:syslog` |
| `vmware` | `vmware:esxlog:apiForwarder` | `vmware:esxlog:source::tcp:1514` | `ops_non_inf_vmw_s` | `vmware:esxlog:apiforwarder` | `net:vmware:esx:syslog` |
| `vmware` | `vmware:esxlog:auto-backup` | `vmware:esxlog:source::tcp:1514` | `ops_non_inf_vmw_s` | `vmware:esxlog:auto-backup` | `net:vmware:esx:syslog` |
| `vmware` | `vmware:esxlog:backup` | `vmware:esxlog:source::tcp:1514` | `ops_non_inf_vmw_s` | `vmware:esxlog:backup` | `net:vmware:esx:syslog` |
| `vmware` | `vmware:esxlog:backup-check` | `vmware:esxlog:source::tcp:1514` | `ops_non_inf_vmw_s` | `vmware:esxlog:backup-check` | `net:vmware:esx:syslog` |
| `vmware` | `vmware:esxlog:backup-ssh` | `vmware:esxlog:source::tcp:1514` | `ops_non_inf_vmw_s` | `vmware:esxlog:backup-ssh` | `net:vmware:esx:syslog` |
| `vmware` | `vmware:esxlog:clusterAgent` | `vmware:esxlog:source::tcp:1514` | `ops_non_inf_vmw_s` | `vmware:esxlog:clusteragent` | `net:vmware:esx:syslog` |
| `vmware` | `vmware:esxlog:configStoreBackup` | `vmware:esxlog:source::tcp:1514` | `ops_non_inf_vmw_s` | `vmware:esxlog:configstorebackup` | `net:vmware:esx:syslog` |
| `vmware` | `vmware:esxlog:crond` | `vmware:esxlog:source::tcp:1514` | `ops_non_inf_vmw_s` | `vmware:esxlog:crond` | `net:vmware:esx:syslog` |
| `vmware` | `vmware:esxlog:crx-cli` | `vmware:esxlog:source::tcp:1514` | `ops_non_inf_vmw_s` | `vmware:esxlog:crx-cli` | `net:vmware:esx:syslog` |
| `vmware` | `vmware:esxlog:envoy` | `vmware:esxlog:source::tcp:1514` | `ops_non_inf_vmw_s` | `vmware:esxlog:envoy` | `net:vmware:esx:syslog` |
| `vmware` | `vmware:esxlog:envoy-access` | `vmware:esxlog:source::tcp:1514` | `ops_non_inf_vmw_s` | `vmware:esxlog:envoy-access` | `net:vmware:esx:syslog` |
| `vmware` | `vmware:esxlog:esxtokend` | `vmware:esxlog:source::tcp:1514` | `ops_non_inf_vmw_s` | `vmware:esxlog:esxtokend` | `net:vmware:esx:syslog` |
| `vmware` | `vmware:esxlog:esxupdate` | `vmware:esxlog:source::tcp:1514` | `ops_non_inf_vmw_s` | `vmware:esxlog:esxupdate` | `net:vmware:esx:syslog` |
| `vmware` | `vmware:esxlog:etcd` | `vmware:esxlog:source::tcp:1514` | `ops_non_inf_vmw_s` | `vmware:esxlog:etcd` | `net:vmware:esx:syslog` |
| `vmware` | `vmware:esxlog:healthd` | `vmware:esxlog:source::tcp:1514` | `ops_non_inf_vmw_s` | `vmware:esxlog:healthd` | `net:vmware:esx:syslog` |
| `vmware` | `vmware:esxlog:healthdPlugins` | `vmware:esxlog:source::tcp:1514` | `ops_non_inf_vmw_s` | `vmware:esxlog:healthdplugins` | `net:vmware:esx:syslog` |
| `vmware` | `vmware:esxlog:heartbeat` | `vmware:esxlog:source::tcp:1514` | `ops_non_inf_vmw_s` | `vmware:esxlog:heartbeat` | `net:vmware:esx:syslog` |
| `vmware` | `vmware:esxlog:hostd-probe` | `vmware:esxlog:source::tcp:1514` | `ops_non_inf_vmw_s` | `vmware:esxlog:hostd-probe` | `net:vmware:esx:syslog` |
| `vmware` | `vmware:esxlog:hostdCgiServer` | `vmware:esxlog:source::tcp:1514` | `ops_non_inf_vmw_s` | `vmware:esxlog:hostdcgiserver` | `net:vmware:esx:syslog` |
| `vmware` | `vmware:esxlog:iofiltervpd` | `vmware:esxlog:source::tcp:1514` | `ops_non_inf_vmw_s` | `vmware:esxlog:iofiltervpd` | `net:vmware:esx:syslog` |
| `vmware` | `vmware:esxlog:kmxa` | `vmware:esxlog:source::tcp:1514` | `ops_non_inf_vmw_s` | `vmware:esxlog:kmxa` | `net:vmware:esx:syslog` |
| `vmware` | `vmware:esxlog:localcli` | `vmware:esxlog:source::tcp:1514` | `ops_non_inf_vmw_s` | `vmware:esxlog:localcli` | `net:vmware:esx:syslog` |
| `vmware` | `vmware:esxlog:nfcd` | `vmware:esxlog:source::tcp:1514` | `ops_non_inf_vmw_s` | `vmware:esxlog:nfcd` | `net:vmware:esx:syslog` |
| `vmware` | `vmware:esxlog:sandboxd` | `vmware:esxlog:source::tcp:1514` | `ops_non_inf_vmw_s` | `vmware:esxlog:sandboxd` | `net:vmware:esx:syslog` |
| `vmware` | `vmware:esxlog:sdrsInjector` | `vmware:esxlog:source::tcp:1514` | `ops_non_inf_vmw_s` | `vmware:esxlog:sdrsinjector` | `net:vmware:esx:syslog` |
| `vmware` | `vmware:esxlog:settingsd` | `vmware:esxlog:source::tcp:1514` | `ops_non_inf_vmw_s` | `vmware:esxlog:settingsd` | `net:vmware:esx:syslog` |
| `vmware` | `vmware:esxlog:snmpd` | `vmware:esxlog:source::tcp:1514` | `ops_non_inf_vmw_s` | `vmware:esxlog:snmpd` | `net:vmware:esx:syslog` |
| `vmware` | `vmware:esxlog:storageRM` | `vmware:esxlog:source::tcp:1514` | `ops_non_inf_vmw_s` | `vmware:esxlog:storagerm` | `net:vmware:esx:syslog` |
| `vmware` | `vmware:esxlog:ucs-tool-esxi-cfg` | `vmware:esxlog:source::tcp:1514` | `ops_non_inf_vmw_s` | `vmware:esxlog:ucs-tool-esxi-cfg` | `net:vmware:esx:syslog` |
| `vmware` | `vmware:esxlog:usbarb` | `vmware:esxlog:source::tcp:1514` | `ops_non_inf_vmw_s` | `vmware:esxlog:usbarb` | `net:vmware:esx:syslog` |
| `vmware` | `vmware:esxlog:vaainasd` | `vmware:esxlog:source::tcp:1514` | `ops_non_inf_vmw_s` | `vmware:esxlog:vaainasd` | `net:vmware:esx:syslog` |
| `vmware` | `vmware:esxlog:vmauthd` | `vmware:esxlog:source::tcp:1514` | `ops_non_inf_vmw_s` | `vmware:esxlog:vmauthd` | `net:vmware:esx:syslog` |
| `vmware` | `vmware:esxlog:vmkernel` | `vmware:esxlog:source::tcp:1514` | `ops_non_inf_vmw_s` | `vmware:esxlog:vmkernel` | `net:vmware:esx:syslog` |
| `vmware` | `vmware:esxlog:vmkmemstats` | `vmware:esxlog:source::tcp:1514` | `ops_non_inf_vmw_s` | `vmware:esxlog:vmkmemstats` | `net:vmware:esx:syslog` |
| `vmware` | `vmware:esxlog:vmkwarning` | `vmware:esxlog:source::tcp:1514` | `ops_non_inf_vmw_s` | `vmware:esxlog:vmkwarning` | `net:vmware:esx:syslog` |
| `vmware` | `vmware:esxlog:vobd` | `vmware:esxlog:source::tcp:1514` | `ops_non_inf_vmw_s` | `vmware:esxlog:vobd` | `net:vmware:esx:syslog` |
| `vmware` | `vmware:esxlog:vsand` | `vmware:esxlog:source::tcp:1514` | `ops_non_inf_vmw_s` | `vmware:esxlog:vsand` | `net:vmware:esx:syslog` |
| `vmware` | `vmware:esxlog:vsansystem` | `vmware:esxlog:source::tcp:1514` | `ops_non_inf_vmw_s` | `vmware:esxlog:vsansystem` | `net:vmware:esx:syslog` |
| `vmware` | `vmware:esxlog:watchdog` | `vmware:esxlog:source::tcp:1514` | `ops_non_inf_vmw_s` | `vmware:esxlog:watchdog` | `net:vmware:esx:syslog` |

## Quarantined — upstream defects to fix

These values could not be classified and are routed to the
quarantine index. Each is a genuine defect in the input
configuration, not a naming choice.

| legacy index | legacy sourcetype | events | reason |
|---|---|---:|---|
| `oracle` | `com.or` | 3 | truncated sourcetype value |
| `oracle` | `com.orac` | 15 | truncated sourcetype value |
| `oracle` | `com.oracle` | 6 | truncated sourcetype value |
| `oracle` | `com.oraclecl` | 2 | truncated sourcetype value |
| `oracle` | `recovery` | 5 | unidentified feed, owner confirmation needed |
| `oracle` | `work` | 8 | unidentified feed, owner confirmation needed |
