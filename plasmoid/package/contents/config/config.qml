import QtQuick
import QtQuick.Controls as Controls
import org.kde.kirigami as Kirigami
import org.kde.kcmutils as KCM

KCM.SimpleKCM {
    id: configPage

    property alias cfg_gatewayHost: gatewayHost.text
    property alias cfg_securityCode: securityCode.text

    Kirigami.FormLayout {
        anchors.left: parent.left
        anchors.right: parent.right

        Controls.TextField {
            id: gatewayHost
            Kirigami.FormData.label: "Gateway IP:"
            placeholderText: "192.168.1.116"
        }

        Controls.TextField {
            id: securityCode
            Kirigami.FormData.label: "Security Code:"
            placeholderText: "Gateway security code (on the bottom)"
            echoMode: Controls.TextField.PasswordEchoOnEdit
        }

        Kirigami.InlineMessage {
            Layout.fillWidth: true
            type: Kirigami.MessageType.Information
            text: "The security code is used only once to generate credentials. After successful connection, it is no longer needed."
            visible: true
        }
    }
}
