import { Constants } from './constant'
import dayjs from 'dayjs'

// 单位换算
export function getScaledValue (value, scale) {
  scale = scale + ''
  scale = parseInt(scale, 10)
  let power = Math.abs(parseInt(scale, 10))

  if (scale > 0) {
    value = value * Math.pow(10, power)
  } else if (scale < 0) {
    value = value / Math.pow(10, power)
  }
  return value
}

/** ********* 解析传感器信息 ********* **/
export function parseSensorData (content) {
  // let dataClone = JSON.parse(JSON.stringify(content.data))
  let sensorData = []
  let severity = {}
  let title = ''
  let tempKeyParts = []
  let customOrder = 0

  for (var key in content.data) {
    if (content.data.hasOwnProperty(key) &&
        content.data[key].hasOwnProperty('Unit')) {
      severity = getSensorStatus(content.data[key])

      if (!content.data[key].hasOwnProperty('CriticalLow')) {
        content.data[key].CriticalLow = '--'
        content.data[key].CriticalHigh = '--'
      }

      if (!content.data[key].hasOwnProperty('WarningLow')) {
        content.data[key].WarningLow = '--'
        content.data[key].WarningHigh = '--'
      }

      tempKeyParts = key.split('/')
      title = tempKeyParts.pop()
      title = tempKeyParts.pop() + '_' + title
      title = title.split('_').map(function (item) {
        return item.toLowerCase().charAt(0).toUpperCase() + item.slice(1)
      })
        .reduce(function (prev, el) {
          return prev + ' ' + el
        })

      content.data[key].Value = getScaledValue(content.data[key].Value, content.data[key].Scale)
      content.data[key].CriticalLow = getScaledValue(content.data[key].CriticalLow, content.data[key].Scale)
      content.data[key].CriticalHigh = getScaledValue(content.data[key].CriticalHigh, content.data[key].Scale)
      content.data[key].WarningLow = getScaledValue(content.data[key].WarningLow, content.data[key].Scale)
      content.data[key].WarningHigh = getScaledValue(content.data[key].WarningHigh, content.data[key].Scale)

      if (Constants.SENSOR_SORT_ORDER.indexOf(
        content.data[key].Unit) > -1) {
        customOrder = Constants.SENSOR_SORT_ORDER.indexOf(content.data[key].Unit)
      } else {
        customOrder = Constants.SENSOR_SORT_ORDER_DEFAULT
      }

      sensorData.push(Object.assign(
        {
          path: key,
          selected: false,
          confirm: false,
          copied: false,
          title: title,
          unit: Constants.SENSOR_UNIT_MAP[content.data[key].Unit],
          severity_flags: severity.flags,
          status: severity.severityText,
          order: severity.order,
          custom_order: customOrder,
          search_text: (title + ' ' + content.data[key].Value + ' ' +
                  Constants.SENSOR_UNIT_MAP[content.data[key].Unit] +
                  ' ' + severity.severityText + ' ' +
                  content.data[key].CriticalLow + ' ' +
                  content.data[key].CriticalHigh + ' ' +
                  content.data[key].WarningLow + ' ' +
                  content.data[key].WarningHigh + ' ').toLowerCase(),
          original_data:
                { key: key, value: content.data[key] }
        },
        content.data[key]))
    }
  }

  return sensorData
}

function getSensorStatus (reading) {
  let severityFlags = {
    critical: false,
    warning: false,
    normal: false
  }

  let severityText = ''
  let order = 0

  if (reading.hasOwnProperty('CriticalLow') && reading.Value < reading.CriticalLow) {
    severityFlags.critical = true
    severityText = 'critical'
    order = 2
  } else if (
    reading.hasOwnProperty('CriticalHigh') &&
    reading.Value > reading.CriticalHigh) {
    severityFlags.critical = true
    severityText = 'critical'
    order = 2
  } else if (
    reading.hasOwnProperty('CriticalLow') &&
    reading.hasOwnProperty('WarningLow') &&
    reading.Value >= reading.CriticalLow &&
    reading.Value <= reading.WarningLow) {
    severityFlags.warning = true
    severityText = 'warning'
    order = 1
  } else if (
    reading.hasOwnProperty('WarningHigh') &&
    reading.hasOwnProperty('CriticalHigh') &&
    reading.Value >= reading.WarningHigh &&
    reading.Value <= reading.CriticalHigh) {
    severityFlags.warning = true
    severityText = 'warning'
    order = 1
  } else {
    severityFlags.normal = true
    severityText = 'normal'
  }
  return {
    flags: severityFlags,
    severityText: severityText,
    order: order
  }
}

/** ********* 单独解析风扇转速信息 ********* **/
export function parseFanRpm (content) {
  let fanInfo = []

  Object.keys(content.data).forEach((key, index) => {
    let sensorType = key.split('/')[4]

    if (sensorType === 'fan_tach') {
      let sensorName = key.split('/')[5]
      fanInfo.push({
        id: index,
        name: sensorName,
        rpm: content.data[key].Value,
        status: 0
      })
    }
  })

  return fanInfo
}

/** ********* 解析固件版本 ********* **/
export function parseFwVersion (content) {
  let isExtended = false
  let bmcActiveVersion = ''
  let hostActiveVersion = ''
  let imageType = ''
  let extendedVersions = []
  let functionalImages = []
  let data = []

  // Get the list of functional images so we can compare
  // later if an image is functional
  if (content.data['/xyz/openbmc_project/software/functional']) {
    functionalImages = content.data['/xyz/openbmc_project/software/functional'].endpoints
  }

  for (let key in content.data) {
    if (content.data.hasOwnProperty(key) &&
        content.data[key].hasOwnProperty('Version')) {
      let activationStatus = ''

      // If the image is "Functional" use that for the
      // activation status, else use the value of
      // "Activation"
      // github.com/openbmc/phosphor-dbus-interfaces/blob/master/xyz/openbmc_project/Software/Activation.interface.yaml
      if (content.data[key].Activation) {
        activationStatus =
            content.data[key].Activation.split('.').pop()
      }

      if (functionalImages.includes(key)) {
        activationStatus = 'Functional'
      }

      imageType = content.data[key].Purpose.split('.').pop()
      isExtended = content.data[key].hasOwnProperty(
        'ExtendedVersion') &&
          content.data[key].ExtendedVersion !== ''
      if (isExtended) {
        extendedVersions = getFormatedExtendedVersions(
          content.data[key].ExtendedVersion)
      }
      data.push(Object.assign(
        {
          path: key,
          activationStatus: activationStatus,
          imageId: key.split('/').pop(),
          imageType: imageType,
          isExtended: isExtended,
          extended:
                { show: false, versions: extendedVersions },
          data: { key: key, value: content.data[key] }
        },
        content.data[key]))

      if (activationStatus === 'Functional' &&
          imageType === 'BMC') {
        bmcActiveVersion = content.data[key].Version
      }

      if (activationStatus === 'Functional' &&
          imageType === 'Host') {
        hostActiveVersion = content.data[key].Version
      }
    }
  }

  return {
    data: data,
    bmcActiveVersion: bmcActiveVersion,
    hostActiveVersion: hostActiveVersion
  }
}

function getFormatedExtendedVersions (extendedVersion) {
  let versions = []
  extendedVersion = extendedVersion.split(',')

  extendedVersion.forEach(function (item) {
    let parts = item.split('-')
    let numberIndex = 0
    for (let i = 0; i < parts.length; i++) {
      if (/[0-9]/.test(parts[i])) {
        numberIndex = i
        break
      }
    }
    let titlePart = parts.splice(0, numberIndex)
    titlePart = titlePart.join('')
    titlePart = titlePart[0].toUpperCase() +
        titlePart.substr(1, titlePart.length)
    let versionPart = parts.join('-')
    versions.push({ title: titlePart, version: versionPart })
  })

  return versions
}
/************************************/

/** ********* 解析网络配置信息 ********* **/
export function parseNetworkData (content) {
  let hostname = ''
  let defaultgateway = ''
  let macAddress = ''

  if (content.data.hasOwnProperty(
    '/xyz/openbmc_project/network/config')) {
    if (content.data['/xyz/openbmc_project/network/config']
      .hasOwnProperty('HostName')) {
      hostname =
        content.data['/xyz/openbmc_project/network/config']
          .HostName
    }
    if (content.data['/xyz/openbmc_project/network/config']
      .hasOwnProperty('DefaultGateway')) {
      defaultgateway =
        content.data['/xyz/openbmc_project/network/config']
          .DefaultGateway
    }
  }

  if (content.data.hasOwnProperty(
    '/xyz/openbmc_project/network/eth0') &&
    content.data['/xyz/openbmc_project/network/eth0']
      .hasOwnProperty('MACAddress')) {
    macAddress =
      content.data['/xyz/openbmc_project/network/eth0']
        .MACAddress
  }

  return {
    data: content.data,
    hostname: hostname,
    defaultgateway: defaultgateway,
    mac_address: macAddress,
    formatted_data: getFormattedData(content)
  }
}

function getFormattedData (content) {
  let data = {
    interface_ids: [],
    interfaces: {},
    ip_addresses: { ipv4: [], ipv6: [] }
  }
  let interfaceId = ''; let keyParts = []; let interfaceHash = ''

  let interfaceType = ''
  for (let key in content.data) {
    if (key.match(/network\/eth\d+(_\d+)?$/ig)) {
      interfaceId = key.split('/').pop()
      if (data.interface_ids.indexOf(interfaceId) === -1) {
        data.interface_ids.push(interfaceId)
        data.interfaces[interfaceId] = {
          interfaceIname: '',
          DomainName: '',
          MACAddress: '',
          Nameservers: [],
          DHCPEnabled: 0,
          ipv4: { ids: [], values: [] },
          ipv6: { ids: [], values: [] }
        }
        data.interfaces[interfaceId].MACAddress =
            content.data[key].MACAddress
        data.interfaces[interfaceId].DomainName =
            content.data[key].DomainName.join(' ')
        data.interfaces[interfaceId].Nameservers =
            content.data[key].Nameservers
        data.interfaces[interfaceId].DHCPEnabled =
            content.data[key].DHCPEnabled
      }
    } else if (
      key.match(
        /network\/eth\d+(_\d+)?\/ipv[4|6]\/[a-z0-9]+$/ig)) {
      keyParts = key.split('/')
      interfaceHash = keyParts.pop()
      interfaceType = keyParts.pop()
      interfaceId = keyParts.pop()

      if (data.interfaces[interfaceId][interfaceType]
        .ids.indexOf(interfaceHash) === -1) {
        data.interfaces[interfaceId][interfaceType]
          .ids.push(interfaceHash)
        data.interfaces[interfaceId][interfaceType]
          .values.push(content.data[key])
        data.ip_addresses[interfaceType].push(
          content.data[key]['Address'])
      }
    }
  }
  return data
}
/************************************/

/** ********* 解析系统日志、信息 ********* **/
export function parseSysLogData (content) {
  let data = []
  let severityCode = ''
  let priority = ''
  let relatedItems = []
  let eventID = 'None'
  let description = 'None'
  let time = ''

  for (var key in content.data) {
    if (content.data.hasOwnProperty(key) &&
        content.data[key].hasOwnProperty('Id')) {
      var severityFlags = {
        low: false,
        medium: false,
        high: false
      }
      severityCode = content.data[key].Severity.split('.').pop()
      priority = Constants.SEVERITY_TO_PRIORITY_MAP[severityCode]
      severityFlags[priority.toLowerCase()] = true
      relatedItems = []
      time = dayjs(content.data[key].Timestamp).format('YYYY-MM-DD HH:mm:ss')
      content.data[key].associations.forEach(function (item) {
        relatedItems.push(item[2])
      })

      if (content.data[key].hasOwnProperty(['EventID'])) {
        eventID = content.data[key].EventID
      }

      if (content.data[key].hasOwnProperty(['Description'])) {
        description = content.data[key].Description
      }

      data.push(Object.assign(
        {
          path: key,
          copied: false,
          priority: priority,
          severity_code: severityCode,
          severity_flags: severityFlags,
          additional_data:
              content.data[key].AdditionalData.join('\n'),
          type: content.data[key].Message,
          selected: false,
          search_text:
              ('#' + content.data[key].Id + ' ' +
                severityCode + ' ' +
                content.data[key].Message + ' ' +
                content.data[key].Severity + ' ' +
                content.data[key].AdditionalData.join(' '))
                .toLowerCase(),
          meta: false,
          confirm: false,
          related_items: relatedItems,
          eventID: eventID,
          description: description,
          time: time,
          data: { key: key, value: content.data[key] }
        },
        content.data[key]))
    }
  }

  return data.sort((a, b) => b.Id - a.Id)
}
/************************************/

/** ********* 解析主机相关信息 ********* **/
function getHost () {
  if (sessionStorage.getItem(Constants.API_CREDENTIALS.host_storage_key) !== null) {
    return sessionStorage.getItem(Constants.API_CREDENTIALS.host_storage_key)
  } else {
    return Constants.API_CREDENTIALS.default_protocol + '://' +
      window.location.hostname +
      (window.location.port ? ':' + window.location.port : '')
  }
}

export function getHostId () {
  let host = getHost()
  return host.replace(/^https?:\/\//ig, '')
}
