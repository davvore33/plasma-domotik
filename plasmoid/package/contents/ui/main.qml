import QtQuick
import QtQuick.Layouts
import QtQuick.Controls as Controls
import org.kde.plasma.plasmoid
import org.kde.kirigami as Kirigami

PlasmoidItem {
    id: root

    property var devices: []
    property bool loading: false
    property bool connected: false
    property string statusText: "Connecting..."
    property string lastError: ""

    property string gatewayHost: "192.168.1.116"
    property string securityCode: ""

    function httpGet(path, callback) {
        var xhr = new XMLHttpRequest()
        xhr.onreadystatechange = function() {
            if (xhr.readyState === XMLHttpRequest.DONE) {
                if (xhr.status === 200) {
                    try {
                        callback(null, JSON.parse(xhr.responseText))
                    } catch(e) {
                        callback(new Error("JSON error"), null)
                    }
                } else {
                    callback(new Error("HTTP " + xhr.status), null)
                }
            }
        }
        xhr.onerror = function() { callback(new Error("Network error"), null) }
        xhr.open("GET", "http://127.0.0.1:8765" + path)
        xhr.send()
    }

    function refreshDevices() {
        root.loading = true
        root.statusText = "Connecting..."

        var connectPath = "/connect?host=" + encodeURIComponent(gatewayHost) + "&securityCode=" + encodeURIComponent(securityCode)

        httpGet(connectPath, function(err, result) {
            if (err || !result || !result.connected) {
                root.loading = false
                root.statusText = "Gateway unreachable"
                if (err) root.lastError = err.message
                root.connected = false
                root.devices = []
                return
            }

            httpGet("/devices", function(err2, result2) {
                root.loading = false
                if (err2) {
                    root.statusText = "Connection error"
                    if (err2) root.lastError = err2.message
                    root.connected = false
                    root.devices = []
                } else {
                    root.devices = result2
                    root.connected = true
                    root.statusText = result2.length + " devices"
                    root.lastError = ""
                }
            })
        })
    }

    function togglePower(deviceId, state) {
        console.log("[PlasmaDomotik] togglePower id=" + deviceId + " state=" + state)
        httpGet("/power?id=" + deviceId + "&state=" + state, function(err, result) {
            console.log("[PlasmaDomotik] power result err=" + err + " result=" + JSON.stringify(result))
            if (!err && result && result.success) delayedRefreshTimer.restart()
        })
    }

    function setColorTemp(deviceId, value) {
        httpGet("/color_temp?id=" + deviceId + "&value=" + value, function(err, result) {
            if (!err && result && result.success) delayedRefreshTimer.restart()
        })
    }

    function setColor(deviceId, hue) {
        httpGet("/color?id=" + deviceId + "&hue=" + hue + "&saturation=100", function(err, result) {
            if (!err && result && result.success) delayedRefreshTimer.restart()
        })
    }

    function setBrightness(deviceId, value) {
        httpGet("/brightness?id=" + deviceId + "&value=" + value, function(err, result) {
            if (!err && result && result.success) delayedRefreshTimer.restart()
        })
    }

    Timer {
        id: delayedRefreshTimer
        interval: 1200
        repeat: false
        onTriggered: refreshDevices()
    }

    Timer {
        interval: 10000
        repeat: true
        running: true
        onTriggered: refreshDevices()
    }

    Component.onCompleted: refreshDevices()

    fullRepresentation: Item {
        implicitWidth: Kirigami.Units.gridUnit * 18
        implicitHeight: Kirigami.Units.gridUnit * 16

        ColumnLayout {
            anchors.fill: parent
            anchors.margins: Kirigami.Units.smallSpacing

            RowLayout {
                Kirigami.Heading {
                    level: 3
                    text: "Plasma Domotik"
                    Layout.fillWidth: true
                }
                Controls.ToolButton {
                    icon.name: "view-refresh"
                    onClicked: refreshDevices()
                }
            }

            Rectangle {
                height: 30
                color: root.connected ? "#4caf50" : (root.loading ? "#ff9800" : "#f44336")
                radius: 4
                Layout.fillWidth: true
                Controls.Label {
                    anchors.centerIn: parent
                    text: root.statusText
                    color: "white"
                }
            }

            Controls.Label { 
                text: "Error: " + root.lastError; 
                color: "red"; 
                visible: root.lastError !== ""; 
                wrapMode: Text.WordWrap 
            }

            Controls.ScrollView {
                Layout.fillWidth: true
                Layout.fillHeight: true
                clip: true

                ListView {
                    width: parent.width
                    model: root.devices

                    delegate: Kirigami.Card {
                        width: ListView.view.width
                        implicitHeight: {
                            const caps = modelData.capabilities || []
                            const sliders = (caps.indexOf("brightness") >= 0 ? 1 : 0)
                                          + (caps.indexOf("color_temp") >= 0 ? 1 : 0)
                                          + (caps.indexOf("color")      >= 0 ? 1 : 0)
                            return Kirigami.Units.gridUnit * (2.5 + sliders * 1.5)
                        }

                        contentItem: ColumnLayout {
                            spacing: Kirigami.Units.smallSpacing

                            RowLayout {
                                Layout.fillWidth: true

                                Kirigami.Icon {
                                    source: modelData.type === "light" ? "flashlight-on" :
                                           modelData.type === "plug" ? "utilities-energy-monitor" : "preferences-system"
                                    implicitWidth: Kirigami.Units.iconSizes.medium
                                    implicitHeight: Kirigami.Units.iconSizes.medium
                                    opacity: modelData.reachable ? 1 : 0.4
                                }
                                ColumnLayout {
                                    Layout.fillWidth: true
                                    Controls.Label { text: modelData.name; font.weight: Font.Medium }
                                    Controls.Label {
                                        text: !modelData.reachable ? "Not reachable" :
                                              (modelData.state && modelData.state.on)
                                                  ? (modelData.capabilities && modelData.capabilities.indexOf("brightness") >= 0
                                                     ? "On · " + (modelData.state.brightness || 0) + "%"
                                                     : "On")
                                                  : "Off"
                                        opacity: 0.6
                                    }
                                }
                                Controls.Switch {
                                    checked: modelData.state && modelData.state.on
                                    enabled: modelData.reachable
                                    onClicked: {
                                        console.log("[PlasmaDomotik] Switch clicked id=" + modelData.id + " currentOn=" + modelData.state.on + " checked=" + checked)
                                        togglePower(modelData.id, !modelData.state.on)
                                    }
                                }
                            }

                            Controls.Slider {
                                visible: modelData.capabilities && modelData.capabilities.indexOf("brightness") >= 0
                                         && modelData.reachable
                                enabled: modelData.state && modelData.state.on
                                Layout.fillWidth: true
                                from: 0
                                to: 100
                                value: modelData.state ? (modelData.state.brightness || 0) : 0
                                onMoved: setBrightness(modelData.id, Math.round(value))
                            }

                            RowLayout {
                                visible: modelData.capabilities && modelData.capabilities.indexOf("color_temp") >= 0
                                         && modelData.reachable
                                Layout.fillWidth: true

                                Controls.Label { text: "☀"; opacity: 0.6; font.pixelSize: 11 }
                                Controls.Slider {
                                    Layout.fillWidth: true
                                    enabled: modelData.state && modelData.state.on
                                    from: 0
                                    to: 100
                                    value: modelData.state ? (100 - (modelData.state.color_temp || 0)) : 50
                                    onMoved: setColorTemp(modelData.id, 100 - Math.round(value))
                                }
                                Controls.Label { text: "❄"; opacity: 0.6; font.pixelSize: 11 }
                            }

                            RowLayout {
                                visible: modelData.capabilities && modelData.capabilities.indexOf("color") >= 0
                                         && modelData.reachable
                                Layout.fillWidth: true

                                Controls.Label { text: "🎨"; opacity: 0.6; font.pixelSize: 11 }
                                Controls.Slider {
                                    Layout.fillWidth: true
                                    enabled: modelData.state && modelData.state.on
                                    from: 0
                                    to: 360
                                    value: modelData.state ? (modelData.state.hue || 0) : 0
                                    onMoved: setColor(modelData.id, Math.round(value))
                                }
                            }
                        }
                    }

                    Controls.Label {
                        anchors.centerIn: parent
                        text: root.loading ? "Loading..." :
                              !root.connected ? "Not connected" : "No devices"
                        opacity: 0.5
                        visible: root.devices.length === 0
                    }
                }
            }
        }
    }
}