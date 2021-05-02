
bose_protocol = Proto("Bose", "Bose protocol")

local report_ids = {
  [0x0c] = "Request",
  [0x0d] = "Response"
}

local noise_levels = {
  [0] = "off",
  [1] = "high",
  [2] = "wind",
  [3] = "low"
}

local auto_off_timeout = {
  [0] = "never",
  [20] = "20",
  [60] = "60",
  [180] = "180"
}

local button_modes = {
  [1] = "alexa",
  [2] = "nc",
  [0x7f] = "error"
}

local firmware_state = {
  [1] = "idle",
  [2] = "ready for transfer",
  [3] = "ready for validate",
  [4] = "ready for run",
  [5] = "complete"
}

local operators = {
  [0] = "Set",
  [1] = "Get",
  [2] = "SetGet",
  [3] = "Status",
  [4] = "Error",
  [5] = "Start",
  [6] = "Result",
  [7] = "Processing"
}

local functions_product_info = {
  [1] = "BMAP version",
  [2] = "Function blocks",
  [3] = "Product ID",
  [4] = "Get functions",
  [5] = "Firmware version",
  [6] = "MAC address",
  [7] = "Serial number",
  [10] = "Hardware revision",
  [11] = "Component devices"
}

local functions_settings = {  
  [2] = "Product name",  
  [3] = "Prompt language",
  [4] = "Auto off",
  [5] = "CNC",
  [6] = "Noise cancelling",
  [7] = "Bass",
  [8] = "Alerts",
  [9] = "Buttons",
  [10] = "Multipoint",
  [11] = "Sidetone",
  [21] = "IMU Volume"
}

local functions_status = {
  [2] = "Battery level",
  [3] = "AUX",
  [4] = "MIC",
  [5] = "Charger"
}

local functions_firmware_upg = {
  [1] = "State",
  [2] = "Init",
  [3] = "Transfer",
  [4] = "Sync",
  [5] = "Validate",
  [6] = "Run",
  [7] = "Reset",
  [8] = "Chunk?"
}

local functions_device_mgmt = {
  [1] = "Connect device",
  [2] = "Disconnect device",
  [3] = "Remove device",
  [4] = "Paired devices",
  [5] = "Device info",
  [6] = "Device info ext.",
  [7] = "Remove all devices",
  [8] = "Pairing",
  [9] = "Local MAC address",
  [10] = "Prepare P2P",
  [11] = "P2P mode",
  [12] = "Routing"
}

local functions_audio_mgmt = {
  [1] = "Source",
  [2] = "Get all",
  [3] = "Control",
  [4] = "Status",
  [5] = "Volume",
  [6] = "Now playing"
}

local function_groups_labels = {
  [0] = "Product info",
  [1] = "Settings",
  [2] = "Status",
  [3] = "Firmware upgrade",
  [4] = "Device management",
  [5] = "Audio management",
  [6] = "Call management",
  [7] = "Control",
  [8] = "Debug",
  [9] = "Notification",  
  [12] = "Hearing assistance",
  [13] = "Data collection",
  [14] = "Heart rate",
  [16] = "Voice assistant",
  [18] = "Firmware",
  [21] = "Augmented reality"
}

local function_groups_functions = {
  [0] = functions_product_info,
  [1] = functions_settings,
  [2] = functions_status,
  [3] = functions_firmware_upg,
  [4] = functions_device_mgmt,
  [5] = functions_audio_mgmt,
}

local f = bose_protocol.fields
f.report_id = ProtoField.uint8("bose.report_id", "Report Id", base.HEX, report_ids)

f.a = ProtoField.bytes("bose.array", "Command")

f.function_group = ProtoField.uint8("bose.function_group", "Function group", base.HEX, function_groups_labels)

f.function_product_info = ProtoField.uint8("bose.function", "Function", base.HEX, functions_product_info)  
f.function_settings = ProtoField.uint8("bose.function", "Function", base.HEX, functions_settings)    
f.function_status = ProtoField.uint8("bose.function", "Function", base.HEX, functions_status)    
f.function_device_mgmt = ProtoField.uint8("bose.function", "Function", base.HEX, functions_device_mgmt)    
f.function_firmwareupg = ProtoField.uint8("bose.function", "Function", base.HEX, functions_firmware_upg)    
f.function_audio_mgmt = ProtoField.uint8("bose.function", "Function", base.HEX, functions_audio_mgmt)    
f.function_other = ProtoField.uint8("bose.function", "Function", base.HEX)

local function_groups_fields = {
  [0] = f.function_product_info,
  [1] = f.function_settings,
  [2] = f.function_status,
  [3] = f.function_firmwareupg,
  [4] = f.function_device_mgmt,
  [5] = f.function_audio_mgmt,
}
    
f.bose_operation = ProtoField.uint8("bose.operation", "Operation", base.HEX, operators)
f.payload_length = ProtoField.uint8("bose.payload_length", "Length", base.DEC)
f.payload = ProtoField.bytes("bose.payload", "Data")
f.remainder = ProtoField.bytes("bose.remainder", "Remainder")

function bose_add_function(buffer, pinfo, tree)
  tree:add(f.function_group, buffer(0, 1))

  local fg = buffer(0, 1):int()

  -- Add function group
  if function_groups_fields[fg] then
    tree:add(function_groups_fields[fg], buffer(1, 1))
  else
    tree:add(f.function_other, buffer(1, 1))
  end

  -- Set info column to label of function
  if function_groups_functions[fg] then
    local funcs = function_groups_functions[fg]
    local function_id = buffer(1, 1):int()

    if funcs[function_id] then
      pinfo.cols.info:append(funcs[function_id])
    else
      pinfo.cols.info:append("?")
      pinfo.cols.info:append(function_groups_labels[fg])
    end
  else
    pinfo.cols.info:append("?")
    pinfo.cols.info:append(function_groups_labels[fg])
  end

  pinfo.cols.info:append(" ")
end




function add_command(buffer, pinfo, tree)
  pinfo.cols.info:append(operators[buffer(2, 1):int()])
  pinfo.cols.info:append(" ")

  subtree = tree:add(f.a, buffer(), "Command")
  bose_add_function(buffer(0, 2), pinfo, subtree)
  subtree:add(f.bose_operation, buffer(2, 1))

  local ll = buffer(3, 1):uint()
  subtree:add(f.payload_length, buffer(3, 1))

  if ll > 0 then
    subtree:add(f.payload, buffer(4, ll))
  end

  if buffer:len() > 4 + ll then
    return buffer(4 + ll)
  else
    return buffer(4 + ll - 1, 0)
  end
end


function bose_protocol.dissector(buffer, pinfo, tree)
  length = buffer:len()
  if length == 0 then return end
  pinfo.cols.protocol = bose_protocol.name
  
  local subtree = tree:add(bose_protocol, buffer(), "Bose protocol")

  local report_id = buffer(0, 1):int()

  subtree:add(f.report_id, buffer(0, 1))

  if report_id == 0x0c then
    pinfo.cols.info:set(">")

    subtree:add(f.payload_length, buffer(1, 2))

    local remainder = buffer(3, buffer(1, 2):int())
    
    while remainder:len() > 0 do
      remainder = add_command(remainder, pinfo, subtree)
    end

    subtree:add(f.remainder, remainder)
  end

  if report_id == 0x0d then
    pinfo.cols.info:set("<")
    pinfo.cols.info:append(operators[buffer(3, 1):int()])
    pinfo.cols.info:append(" ")

    bose_add_function(buffer(1, 2), pinfo, subtree)
    subtree:add(f.bose_operation, buffer(3, 1))
    subtree:add(f.payload_length, buffer(4, 1))
    subtree:add(f.payload, buffer(5, buffer(4, 1):int()))  
    subtree:add(f.remainder, buffer(5 + buffer(4, 1):int()))
  end
end

DissectorTable.get("usb.interrupt"):add(0x03, bose_protocol)
