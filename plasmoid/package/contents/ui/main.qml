import QtQuick
import QtQuick.Layouts
import QtQuick.Controls as Controls
import org.kde.plasma.plasmoid
import org.kde.plasma.components as PlasmaComponents
import org.kde.kirigami as Kirigami

PlasmoidItem {
    id: root

    property var devices: []
    property bool loading: false
    property bool connected: false
    property string statusText: "Connecting..."

    preferredRepresentation: Plasmoid.compactRepresentation
    compactRepresentation: compactLayout
    fullRepresentation: fullLayout

    plasmoid.configurationChanged: {
        refreshDevices();
    }

    // HTTP helper
    function httpGet(path, callback) {
        var xhr = new XMLHttpRequest();
        xhr.onreadystatechange = function() {
            if (xhr.readyState === XMLHttpRequest.DONE) {
                if (xhr.status === 200) {
                    callback(null, JSON.parse(xhr.responseText));
                } else {
                    callback(new Error("HTTP " + xhr.status), null);
                }
            }
        };
        xhr.open("GET", "http://127.0.0.1:8765" + path);
        xhr.send();
    }

    function refreshDevices() {
        loading = true;
        var host = plasmoid.configuration.gatewayHost;
        var code = plasmoid.configuration.securityCode;

        var connectPath = "/connect";
        if (code && host) {
            connectPath = "/connect?host=" + encodeURIComponent(host) + "&securityCode=" + encodeURIComponent(code);
        }

        httpGet(connectPath, function(err, result) {
            if (err || !result || !result.connected) {
                loading = false;
                statusText = "Gateway unreachable";
                connected = false;
                devices = [];
                return;
            }

            httpGet("/devices", function(err2, result2) {
                loading = false;
                if (err2) {
                    statusText = "Connection error";
                    connected = false;
                    devices = [];
                } else {
                    devices = result2;
                    connected = true;
                    statusText = devices.length + " devices";
                }
            });
        });
    }

    function togglePower(deviceId, state) {
        httpGet("/power?id=" + deviceId + "&state=" + state, function(err, result) {
            if (!err && result && result.success) {
                refreshDevices();
            }
        });
    }

    Component.onCompleted: {
        plasmoid.busy = loading;
        refreshDevices();
    }

    onLoadingChanged: {
        plasmoid.busy = loading;
    }

    // Compact representation (panel icon)
    Item {
        id: compactLayout

        Kirigami.Icon {
            anchors.centerIn: parent
            source: connected ? "lightbulb" : "network-offline"
            implicitWidth: Math.min(parent.width, parent.height)
            implicitHeight: Math.min(parent.width, parent.height)
        }

        MouseArea {
            anchors.fill: parent
            onClicked: plasmoid.expanded = !plasmoid.expanded
        }
    }

    // Full representation (popup)
    Item {
        id: fullLayout
        implicitWidth: Kirigami.Units.gridUnit * 20
        implicitHeight: Kirigami.Units.gridUnit * 25

        ColumnLayout {
            anchors.fill: parent
            anchors.margins: Kirigami.Units.smallSpacing
            spacing: Kirigami.Units.smallSpacing

            // Header
            RowLayout {
                Layout.fillWidth: true

                Kirigami.Heading {
                    level: 3
                    text: "Plasma Domotik"
                    Layout.fillWidth: true
                }

                Controls.Button {
                    icon.name: "view-refresh"
                    flat: true
                    onClicked: refreshDevices()
                    enabled: !loading
                }
            }

            // Status
            PlasmaComponents.Label {
                text: statusText
                opacity: 0.7
                Layout.fillWidth: true
            }

            // Device list
            ListView {
                Layout.fillWidth: true
                Layout.fillHeight: true
                model: devices
                spacing: Kirigami.Units.smallSpacing

                delegate: Rectangle {
                    width: ListView.view.width
                    height: Kirigami.Units.gridUnit * 2
                    color: Kirigami.Theme.backgroundColor
                    radius: Kirigami.Units.smallSpacing

                    RowLayout {
                        anchors.fill: parent
                        anchors.leftMargin: Kirigami.Units.smallSpacing
                        anchors.rightMargin: Kirigami.Units.smallSpacing
                        spacing: Kirigami.Units.smallSpacing

                        Kirigami.Icon {
                            source: {
                                if (modelData.type === "light") return "lightbulb";
                                if (modelData.type === "plug") return "plug";
                                if (modelData.type === "blind") return "window";
                                return "preferences-system";
                            }
                            implicitWidth: Kirigami.Units.iconSizes.smallMedium
                            implicitHeight: Kirigami.Units.iconSizes.smallMedium
                            opacity: modelData.reachable ? 1.0 : 0.4
                        }

                        ColumnLayout {
                            Layout.fillWidth: true
                            spacing: 0

                            PlasmaComponents.Label {
                                text: modelData.name
                                font.weight: Font.Medium
                            }

                            PlasmaComponents.Label {
                                text: {
                                    if (!modelData.reachable) return "Not reachable";
                                    if (modelData.state && modelData.state.on !== undefined) {
                                        return modelData.state.on ? "On" : "Off";
                                    }
                                    return modelData.type;
                                }
                                font.pixelSize: Kirigami.Theme.smallFont.pixelSize
                                opacity: 0.6
                            }
                        }

                        Controls.Switch {
                            checked: modelData.state && modelData.state.on
                            enabled: modelData.reachable
                            onCheckStateChanged: {
                                togglePower(modelData.id, checked);
                            }
                        }
                    }
                }

                // Empty state
                Label {
                    anchors.centerIn: parent
                    text: {
                        if (loading) return "Loading devices...";
                        if (!connected) return "Not connected to gateway";
                        return "No devices found";
                    }
                    opacity: 0.5
                    visible: devices.length === 0
                }
            }
        }
    }
}
