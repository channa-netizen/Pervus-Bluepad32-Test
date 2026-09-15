from pathlib import Path
import sys
p=Path("components/bluepad32/bt/uni_bt_le.c")
s=p.read_text()

old = '        status = hids_client_disconnect(device->hids_cid);\\n        if (status != ERROR_CODE_SUCCESS) {\\n            loge("Failed to disconnect HIDS client for hids_cid=%d, status=%d\\\\n", device->hids_cid, status);\\n        }'
new = '        if (device->hids_cid != 0 && device->hids_cid != 0xffff) {\\n            status = hids_client_disconnect(device->hids_cid);\\n            if (status != ERROR_CODE_SUCCESS) {\\n                loge("[PERVUS BLE] HIDS disconnect failed: handle=0x%04x hids_cid=%d status=%d\\\\n", con_handle, device->hids_cid, status);\\n            }\\n        } else {\\n            logi("[PERVUS BLE] SKIP invalid HIDS disconnect: handle=0x%04x hids_cid=%d\\\\n", con_handle, device->hids_cid);\\n        }'
old=old.replace('\\n','\n')
new=new.replace('\\n','\n')
if old not in s: sys.exit("hids baseline not found")
s=s.replace(old,new,1)

old = '    gap_event_advertising_report_get_address(packet, addr);\\n    if (uni_hid_device_get_instance_for_address(addr)) {\\n        // Ignore, address already found\\n        return;\\n    }'.replace('\\n','\n')
new = '    gap_event_advertising_report_get_address(packet, addr);\\n    uni_hid_device_t* existing = uni_hid_device_get_instance_for_address(addr);\\n    if (existing) {\\n        logi("[PERVUS BLE] DUP ADV addr=%s connected=%d state=%d handle=0x%04x hids_cid=%d\\\\n",\\n             bd_addr_to_str(addr), existing->conn.connected, existing->conn.state, existing->conn.handle, existing->hids_cid);\\n        // Diagnostic only: preserve 4.1.0 behavior. Do not replace/delete.\\n        return;\\n    }'.replace('\\n','\n')
if old not in s: sys.exit("advertisement baseline not found")
s=s.replace(old,new,1)

old = '        case SM_EVENT_PAIRING_COMPLETE:\\n            sm_event_pairing_complete_get_address(packet, addr);\\n            device = uni_hid_device_get_instance_for_address(addr);'.replace('\\n','\n')
new = '        case SM_EVENT_PAIRING_COMPLETE:\\n            sm_event_pairing_complete_get_address(packet, addr);\\n            logi("[PERVUS BLE] PAIRING_COMPLETE addr=%s handle=0x%04x status=0x%02x\\\\n", bd_addr_to_str(addr), sm_event_pairing_complete_get_handle(packet), sm_event_pairing_complete_get_status(packet));\\n            device = uni_hid_device_get_instance_for_address(addr);'.replace('\\n','\n')
if old not in s: sys.exit("pairing baseline not found")
s=s.replace(old,new,1)

p.write_text(s)
print("PERVUS diagnostic patch applied")
