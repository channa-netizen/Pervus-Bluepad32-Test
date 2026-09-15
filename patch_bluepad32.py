from pathlib import Path

ROOT = Path(".")
matches = list(ROOT.rglob("uni_bt_le.c"))

if not matches:
    raise SystemExit("ERROR: uni_bt_le.c not found")

print("Found uni_bt_le.c files:")
for p in matches:
    print(" -", p)

# Prefer the Bluepad32 source copy
targets = [
    p for p in matches
    if "bluepad32" in str(p).lower()
]

if not targets:
    raise SystemExit("ERROR: Bluepad32 uni_bt_le.c not found")

src = targets[0]
print(f"\nPatching: {src}")

text = src.read_text(encoding="utf-8")


# ---------------------------------------------------------
# PATCH 1
# Guard invalid HIDS CID
# ---------------------------------------------------------

old = """    if (device) {
        status = hids_client_disconnect(device->hids_cid);
        if (status != ERROR_CODE_SUCCESS) {
            loge("Failed to disconnect HIDS client for hids_cid=%d, status=%d\\n", device->hids_cid, status);
        }
        // gap_delete_bonding(0, device->conn.btaddr);
    }
"""

new = """    if (device) {
        if (device->hids_cid != 0 && device->hids_cid != 0xffff) {
            logi("[PERVUS BLE] HIDS disconnect con_handle=%#x hids_cid=%d\\n",
                 con_handle, device->hids_cid);

            status = hids_client_disconnect(device->hids_cid);

            if (status != ERROR_CODE_SUCCESS) {
                loge("[PERVUS BLE] Failed HIDS disconnect hids_cid=%d status=%d\\n",
                     device->hids_cid, status);
            }
        } else {
            logi("[PERVUS BLE] SKIP invalid HIDS disconnect con_handle=%#x hids_cid=%d\\n",
                 con_handle, device->hids_cid);
        }

        // gap_delete_bonding(0, device->conn.btaddr);
    }
"""

if old not in text:
    raise SystemExit("ERROR: hog_disconnect baseline not found")

text = text.replace(old, new, 1)
print("PATCH 1 OK: HIDS CID guard")


# ---------------------------------------------------------
# PATCH 2
# Log duplicate advertisements without changing behavior
# ---------------------------------------------------------

old = """    gap_event_advertising_report_get_address(packet, addr);
    if (uni_hid_device_get_instance_for_address(addr)) {
        // Ignore, address already found
        return;
    }
"""

new = """    gap_event_advertising_report_get_address(packet, addr);

    uni_hid_device_t* existing =
        uni_hid_device_get_instance_for_address(addr);

    if (existing) {
        logi("[PERVUS BLE] DUP ADV addr=%s connected=%d state=%d handle=%#x hids_cid=%d\\n",
             bd_addr_to_str(addr),
             existing->conn.connected,
             existing->conn.state,
             existing->conn.handle,
             existing->hids_cid);

        // Diagnostic only:
        // preserve original Bluepad32 4.1.0 behavior.
        return;
    }
"""

if old not in text:
    raise SystemExit("ERROR: advertising baseline not found")

text = text.replace(old, new, 1)
print("PATCH 2 OK: duplicate advertisement logging")


# ---------------------------------------------------------
# PATCH 3
# Log pairing-complete lifecycle
# ---------------------------------------------------------

old = """        case SM_EVENT_PAIRING_COMPLETE:
            sm_event_pairing_complete_get_address(packet, addr);
            device = uni_hid_device_get_instance_for_address(addr);
"""

new = """        case SM_EVENT_PAIRING_COMPLETE:
            sm_event_pairing_complete_get_address(packet, addr);

            logi("[PERVUS BLE] PAIRING_COMPLETE addr=%s handle=%#x status=%#x\\n",
                 bd_addr_to_str(addr),
                 sm_event_pairing_complete_get_handle(packet),
                 sm_event_pairing_complete_get_status(packet));

            device = uni_hid_device_get_instance_for_address(addr);
"""

if old not in text:
    raise SystemExit("ERROR: pairing baseline not found")

text = text.replace(old, new, 1)
print("PATCH 3 OK: pairing logging")


# ---------------------------------------------------------
# SAVE + VERIFY
# ---------------------------------------------------------

src.write_text(text, encoding="utf-8")

verify = src.read_text(encoding="utf-8")

count = verify.count("[PERVUS BLE]")

print(f"\nPERVUS diagnostic markers found: {count}")

if count < 4:
    raise SystemExit(
        f"ERROR: expected at least 4 PERVUS markers, found {count}"
    )

if "device->hids_cid != 0 && device->hids_cid != 0xffff" not in verify:
    raise SystemExit("ERROR: HIDS CID guard verification failed")

if "[PERVUS BLE] DUP ADV" not in verify:
    raise SystemExit("ERROR: DUP ADV verification failed")

if "[PERVUS BLE] PAIRING_COMPLETE" not in verify:
    raise SystemExit("ERROR: PAIRING_COMPLETE verification failed")

print("\n======================================")
print(" PERVUS BLUEPAD32 PATCH SUCCESSFUL")
print("======================================")
print(src)
