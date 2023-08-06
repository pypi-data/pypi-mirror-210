from dataclasses import dataclass
from typing import Any, List, TypedDict


@dataclass
class Template:
    params: Any  # Python TypedDict ile dict'i eşleştiremiyor
    channel: str
    err_code: str
    _header: str
    _text: str

    @property
    def message(self) -> str:
        _message = self._text.format(**self.params)
        return _message

    @property
    def header(self) -> str:
        return self._header

    @property
    def blocks(self) -> List[dict]:
        return [{}]


class FutureOrderParams(TypedDict):
    building_name: str
    brand_name: str
    adisyon_no: str
    platform: str


@dataclass
class FutureOrderTemplate(Template):
    params: FutureOrderParams
    channel: str
    _header: str = ":information_source: İleri Tarihli Sipariş Geldi."
    _text: str = "*{building_name}* binasında bulunan *{brand_name}* markasına *{adisyon_no}* adisyon nolu *{platform}* üzerinden ileri \
tarihli bir sipariş geldi ancak teslimat saati bilinmiyor. Lütfen *{platform}* ile iletişime geçiniz ve aldığınız uyarı \
mesajının kodunu yazılım-destek kanalına iletiniz. (ERR-0002)"

    @property
    def blocks(self) -> List[dict]:
        return [
            {
                "type": "header",
                "text": {
                    "type": "plain_text",
                    "text": self.header,
                    "emoji": True,
                },
            },
            {"type": "divider"},
            {
                "type": "section",
                "text": {"type": "mrkdwn", "text": self.message},
                "accessory": {
                    "type": "image",
                    "image_url": "https://s3-media2.fl.yelpcdn.com/bphoto/DawwNigKJ2ckPeDeDM7jAg/o.jpg",
                    "alt_text": "brand logo",
                },
            },
            {
                "type": "section",
                "text": {"type": "mrkdwn", "text": f"*Hata Kodu*: {self.err_code}"},
            },
        ]


class NoOrdersFromBrandParams(TypedDict):
    log_id: str
    function_name: str


@dataclass
class NoOrdersFromBrandTemplate(Template):
    params: NoOrdersFromBrandParams
    channel: str
    _header: str = ":skull: Hiçbir markadan sipariş alınamayacak"
    _text: str = "Acil işlem yapınız ! log_id: {log_id}, function_name: {function_name}"

    @property
    def blocks(self) -> List[dict]:
        return [
            {
                "type": "header",
                "text": {
                    "type": "plain_text",
                    "text": self.header,
                    "emoji": True,
                },
            },
            {"type": "divider"},
            {
                "type": "section",
                "text": {"type": "mrkdwn", "text": self.message},
            },
            {
                "type": "section",
                "text": {"type": "mrkdwn", "text": f"*Hata Kodu*: {self.err_code}"},
            },
        ]


class CantSaveOrderParams(TypedDict):
    brand_name: str
    platform_code: str
    platform: str


@dataclass
class CantSaveOrderTemplate(Template):
    params: CantSaveOrderParams
    channel: str
    _header: str = ":exclamation: Sipariş Sisteme Kaydedilemedi"
    _text: str = (
        "Eksik sipariş içeriği nedeniyle  *{brand_name}* markasına gelen *{platform_code}* platform kodlu "
        "sipariş sisteme kaydedilemedi. Bu sipariş ile ilgili aldığınız uyarı mesajı kodunu yazılım-destek "
        "kanalına iletiniz ve *{platform}* ile iletişime geçiniz."
    )

    @property
    def blocks(self) -> List[dict]:
        return [
            {
                "type": "header",
                "text": {
                    "type": "plain_text",
                    "text": self.header,
                    "emoji": True,
                },
            },
            {"type": "divider"},
            {
                "type": "section",
                "text": {"type": "mrkdwn", "text": self.message},
                "accessory": {
                    "type": "image",
                    "image_url": "https://s3-media2.fl.yelpcdn.com/bphoto/DawwNigKJ2ckPeDeDM7jAg/o.jpg",
                    "alt_text": "alt text for image",
                },
            },
            {
                "type": "section",
                "text": {"type": "mrkdwn", "text": f"*Hata Kodu*: {self.err_code}"},
            },
        ]


class OrderCantConfirmedParams(TypedDict):
    building_name: str
    brand_name: str
    adisyon_no: str
    platform: str


@dataclass
class OrderCantConfirmedTemplate(Template):
    params: OrderCantConfirmedParams
    channel: str
    _header: str = ":exclamation: Platforma Siparişin Onaylandığı Bilgisi Gönderilemedi"
    _text: str = "*{building_name}* binasında bulunan *{brand_name}* markasındaki *{adisyon_no}* adisyon numaralı  \
                 siparişin onaylandığı bilgisi *{platform}* platformuna iletilemedi. Bu sipariş ile ilgili aldığınız  \
                 uyarı mesajı kodunu yazılım-destek kanalına iletiniz ve {platform} ile iletişime geçiniz."

    @property
    def blocks(self) -> List[dict]:
        return [
            {
                "type": "header",
                "text": {
                    "type": "plain_text",
                    "text": self.header,
                    "emoji": True,
                },
            },
            {"type": "divider"},
            {
                "type": "section",
                "text": {"type": "mrkdwn", "text": self.message},
                "accessory": {
                    "type": "image",
                    "image_url": "https://s3-media2.fl.yelpcdn.com/bphoto/DawwNigKJ2ckPeDeDM7jAg/o.jpg",
                    "alt_text": "alt text for image",
                },
            },
            {
                "type": "section",
                "text": {"type": "mrkdwn", "text": f"*Hata Kodu*: {self.err_code}"},
            },
        ]


class PlatformConnectionFailedParams(TypedDict):
    log_id: str
    function_name: str


@dataclass
class PlatformConnectionsFailedTemplate(Template):
    params: PlatformConnectionFailedParams
    channel: str
    _header: str = ":skull: Bazı Markaların Platform Bağlantısı Sağlanamadı"
    _text: str = """
    Acil işlem yapınız ! log_id: {log_id}, function_name: {function_name}
    """

    @property
    def blocks(self) -> List[dict]:
        return [
            {
                "type": "header",
                "text": {
                    "type": "plain_text",
                    "text": self.header,
                    "emoji": True,
                },
            },
            {"type": "divider"},
            {
                "type": "section",
                "text": {"type": "mrkdwn", "text": self.message},
            },
            {
                "type": "section",
                "text": {"type": "mrkdwn", "text": f"*Hata Kodu*: {self.err_code}"},
            },
        ]


class OrderStatusNotCommunicatedToCustomerParams(TypedDict):
    building_name: str
    brand_name: str
    adisyon_no: str
    platform: str


@dataclass
class OrderStatusNotCommunicatedToCustomer(Template):
    params: OrderStatusNotCommunicatedToCustomerParams
    channel: str
    _header: str = ":exclamation: Müşteriye Sipariş Durum Güncellemesi İletilmedi"
    _text: str = "*{building_name}* binasında bulunan *{brand_name}* markasına gelene *{adisyon_no}* adisyon numaralı  \
sipariş *{platform}* platformu üzerinde güncellenmedi. Aldığınız uyarı mesajın kodunu yazılım-destek kanalına iletiniz."

    @property
    def blocks(self) -> Any:
        return [
            {
                "type": "header",
                "text": {
                    "type": "plain_text",
                    "text": self.header,
                    "emoji": True,
                },
            },
            {"type": "divider"},
            {
                "type": "section",
                "text": {"type": "mrkdwn", "text": self.message},
                "accessory": {
                    "type": "image",
                    "image_url": "https://s3-media2.fl.yelpcdn.com/bphoto/DawwNigKJ2ckPeDeDM7jAg/o.jpg",
                    "alt_text": "brand logo",
                },
            },
            {
                "type": "section",
                "text": {"type": "mrkdwn", "text": f"*Hata Kodu*: {self.err_code}"},
            },
        ]


class OrderValidationParams(TypedDict):
    restaurant_id: str
    order_id: str
    platform: str


@dataclass
class OrderValidation(Template):
    params: OrderValidationParams
    channel: str
    _header: str = ":exclamation: Sipariş Güncellenemedi"
    _text: str = "*{restaurant_id}* restoran koduna sahip restoranın platform kodu *{order_id}* olan siparişi *{platform}* \
    platformunda güncellenirken validasyon hatası oluştu, lütfen yazılım destek kanalı ile iletişime geçiniz."

    @property
    def blocks(self) -> Any:
        return [
            {
                "type": "header",
                "text": {
                    "type": "plain_text",
                    "text": self.header,
                    "emoji": True,
                },
            },
            {"type": "divider"},
            {
                "type": "section",
                "text": {"type": "mrkdwn", "text": self.message},
                "accessory": {
                    "type": "image",
                    "image_url": "https://s3-media2.fl.yelpcdn.com/bphoto/DawwNigKJ2ckPeDeDM7jAg/o.jpg",
                    "alt_text": "brand logo",
                },
            },
            {
                "type": "section",
                "text": {"type": "mrkdwn", "text": f"*Hata Kodu*: {self.err_code}"},
            },
        ]


class GettingPermissionParams(TypedDict):
    log_id: str


@dataclass
class GettingPermission(Template):
    params: GettingPermissionParams
    channel: str
    _header: str = ":exclamation: Yetki Çekme Hatası"
    _text: str = "Yetkileri çekme isteğinde hata oluştu sistem kullanımında sorun oluşacaktır. Hata Kodu: *{log_id}*"

    @property
    def blocks(self) -> Any:
        return [
            {
                "type": "header",
                "text": {
                    "type": "plain_text",
                    "text": self.header,
                    "emoji": True,
                },
            },
            {"type": "divider"},
            {
                "type": "section",
                "text": {"type": "mrkdwn", "text": self.message},
            },
            {
                "type": "section",
                "text": {"type": "mrkdwn", "text": f"*Hata Kodu*: {self.err_code}"},
            },
        ]


class PrintAdisyonParams(TypedDict):
    building_name: str
    brand_name: str


@dataclass
class PrintAdisyon(Template):
    params: PrintAdisyonParams
    channel: str
    _header: str = ":exclamation: Adisyon Yazdırma Hatası"
    _text: str = "*{building_name}* binasında bulunan *{brand_name}* markasında adisyon yazdırma ile ilgili problem var.  \
Öncelikle Anasayfada bulunan Mutfak Paneli altındaki Yazdırma Testini yapınız. Yazıcıda bir problem yoksa  \
yazılım-destek ile iletişime geçiniz."

    @property
    def blocks(self) -> Any:
        return [
            {
                "type": "header",
                "text": {
                    "type": "plain_text",
                    "text": self.header,
                    "emoji": True,
                },
            },
            {"type": "divider"},
            {
                "type": "section",
                "text": {"type": "mrkdwn", "text": self.message},
            },
            {
                "type": "section",
                "text": {"type": "mrkdwn", "text": f"*Hata Kodu*: {self.err_code}"},
            },
        ]


class PrintTestAdisyonParams(TypedDict):
    building_name: str
    brand_name: str


@dataclass
class PrintTestAdisyon(Template):
    params: PrintTestAdisyonParams
    channel: str
    _header: str = ":exclamation: Test Adisyon Yazdırma Hatası"
    _text: str = "*{building_name}* binasında bulunan *{brand_name}* markasında test adisyon yazdırma ile ilgili \
                 problem var. Lütfen yazıcı bağlantılarınızı, adisyon kağıdını vb. kontrolleri yapınız."

    @property
    def blocks(self) -> Any:
        return [
            {
                "type": "header",
                "text": {
                    "type": "plain_text",
                    "text": self.header,
                    "emoji": True,
                },
            },
            {"type": "divider"},
            {
                "type": "section",
                "text": {"type": "mrkdwn", "text": self.message},
            },
            {
                "type": "section",
                "text": {"type": "mrkdwn", "text": f"*Hata Kodu*: {self.err_code}"},
            },
        ]


class AdisyonCounterParams(TypedDict):
    name: str
    surname: str
    print_time: str
    order_id: str
    building_name: str
    brand_name: str
    brand_id: str
    log_id: str


@dataclass
class AdisyonCounter(Template):
    params: AdisyonCounterParams
    channel: str
    _header: str = ":exclamation: Adisyon Yazdırma Sayısı Artırma Hatası"
    _text: str = "*Kullanıcı Adı*: {name} \n*Kullanıcı Soyadı*: {surname}\n*Yazdırma zamanı*: {print_time}\n* \
                 Sipariş numarası*: {order_id}\n*Bina Adı*: {building_name}\n*Marka Adı*: {brand_name}\n*Marka ID*:  \
                 {brand_id}\n*Log ID*: {log_id}"

    @property
    def blocks(self) -> Any:
        return [
            {
                "type": "header",
                "text": {
                    "type": "plain_text",
                    "text": self.header,
                    "emoji": True,
                },
            },
            {"type": "divider"},
            {
                "type": "section",
                "text": {"type": "mrkdwn", "text": self.message},
            },
            {
                "type": "section",
                "text": {"type": "mrkdwn", "text": f"*Hata Kodu*: {self.err_code}"},
            },
        ]


class CheckPlatformConnectionParams(TypedDict):
    platform: str
    building_name: str
    brand_name: str


@dataclass
class CheckPlatformConnection(Template):
    params: CheckPlatformConnectionParams
    channel: str
    _header: str = ":exclamation: {platform} Bağlantısını Kontrol Et"
    _text: str = "*{building_name}* binasında bulunan *{brand_name}* markasının *{platform}* bağlantısında problem  \
                 olabilir. Lütfen, Bina Yönetim Paneli, Sipariş Akış - Platform Durum Sayfasından, iletilen marka için  \
                 Satış Kanalının açık/kapalı olduğunu kontrol ediniz. Açık olmasına rağmen bağlantı problemi devam  \
                 ediyorsa, *{platform}* ile  iletişime geçiniz. "

    @property
    def blocks(self) -> Any:
        return [
            {
                "type": "header",
                "text": {
                    "type": "plain_text",
                    "text": self.header.format(platform=self.params.get("platform", "")),
                    "emoji": True,
                },
            },
            {"type": "divider"},
            {
                "type": "section",
                "text": {"type": "mrkdwn", "text": self.message},
            },
            {
                "type": "section",
                "text": {"type": "mrkdwn", "text": f"*Hata Kodu*: {self.err_code}"},
            },
        ]


class FailedToAddBrandConfigInformationParams(TypedDict):
    platform: str
    brand_name: str
    building_name: str


@dataclass
class FailedToAddBrandConfigInformation(Template):
    params: FailedToAddBrandConfigInformationParams
    channel: str
    _header: str = ":exclamation: Yeni Markanın Platform Bilgileri Sisteme Eklenemedi."
    _text: str = "Lütfen *Üye Listesi* ekranından *{building_name}* binasında bulunan *{brand_name}* markası ve  \
                 *{platform}* platformu için API bağlantı bilgilerini kontrol ediniz. Bilgilerin doğruluğunu kontrol  \
                 ettikten sonra yazılım-destek ile iletişime geçiniz."

    @property
    def blocks(self) -> Any:
        return [
            {
                "type": "header",
                "text": {
                    "type": "plain_text",
                    "text": self.header,
                    "emoji": True,
                },
            },
            {"type": "divider"},
            {
                "type": "section",
                "text": {"type": "mrkdwn", "text": self.message},
            },
            {
                "type": "section",
                "text": {"type": "mrkdwn", "text": f"*Hata Kodu*: {self.err_code}"},
            },
        ]


class OrderStatusNotCommunicatedToPlatformParams(TypedDict):
    building_name: str
    brand_name: str
    order_id: str
    platform: str
    status: str


@dataclass
class OrderStatusNotCommunicatedToPlatform(Template):
    params: OrderStatusNotCommunicatedToPlatformParams
    channel: str
    _header: str = ":exclamation: Siparişin Statü Güncellemesi Platforma İletilemedi"
    _text: str = "*{building_name}* binasında bulunan *{brand_name}* markasının *{order_id}* numaralı siparişi  \
                 *{platform}* platformunda *{status}* durumuna geçemedi."

    @property
    def blocks(self) -> Any:
        return [
            {
                "type": "header",
                "text": {
                    "type": "plain_text",
                    "text": self.header,
                    "emoji": True,
                },
            },
            {"type": "divider"},
            {
                "type": "section",
                "text": {"type": "mrkdwn", "text": self.message},
                "accessory": {
                    "type": "image",
                    "image_url": "https://s3-media2.fl.yelpcdn.com/bphoto/DawwNigKJ2ckPeDeDM7jAg/o.jpg",
                    "alt_text": "brand logo",
                },
            },
            {
                "type": "section",
                "text": {"type": "mrkdwn", "text": f"*Hata Kodu*: {self.err_code}"},
            },
        ]


class InvalidOrderStatusParams(TypedDict):
    building_name: str
    brand_name: str
    order_id: str
    platform: str
    status: str


@dataclass()
class InvalidOrderStatus(Template):
    params: InvalidOrderStatusParams
    channel: str
    _header: str = ":exclamation: Siparişin Statü Güncellemesi Platforma İletilemedi"
    _text: str = "*{building_name}* binasında bulunan *{brand_name}* markasının *{order_id}* numaralı siparişi  \
                     *{platform}* platformunda *{status}* durumunun bir karşılığı bulunamadı!"

    @property
    def blocks(self) -> Any:
        return [
            {
                "type": "header",
                "text": {
                    "type": "plain_text",
                    "text": self.header,
                    "emoji": True,
                },
            },
            {"type": "divider"},
            {
                "type": "section",
                "text": {"type": "mrkdwn", "text": self.message},
                "accessory": {
                    "type": "image",
                    "image_url": "https://s3-media2.fl.yelpcdn.com/bphoto/DawwNigKJ2ckPeDeDM7jAg/o.jpg",
                    "alt_text": "brand logo",
                },
            },
            {
                "type": "section",
                "text": {"type": "mrkdwn", "text": f"*Hata Kodu*: {self.err_code}"},
            },
        ]


class OrderContentCouldNotBeConvertedPMFormatParams(TypedDict):
    building_name: str
    brand_name: str
    platform_code: str
    platform: str


@dataclass
class OrderContentCouldNotBeConvertedPMFormatTemplate(Template):
    params: CantSaveOrderParams
    channel: str
    _header: str = ":exclamation: Sipariş İçeriği Paket Mutfak Formatına Çevrilemedi"
    _text: str = "*{building_name}* binasında bulunan *{brand_name}* markasına ait *{platform}* platformundan gelen \
        *{platform_code}* platform kodlu sipariş içeriği Paket Mutfak formatına çevrilemedi. Bu sipariş ile ilgili \
        aldığınız uyarı mesajı kodunu yazılım-destek kanalına iletiniz ve *{platform}* ile iletişime geçiniz."

    @property
    def blocks(self) -> List[dict]:
        return [
            {
                "type": "header",
                "text": {
                    "type": "plain_text",
                    "text": self.header,
                    "emoji": True,
                },
            },
            {"type": "divider"},
            {
                "type": "section",
                "text": {"type": "mrkdwn", "text": self.message},
                "accessory": {
                    "type": "image",
                    "image_url": "https://s3-media2.fl.yelpcdn.com/bphoto/DawwNigKJ2ckPeDeDM7jAg/o.jpg",
                    "alt_text": "alt text for image",
                },
            },
            {
                "type": "section",
                "text": {"type": "mrkdwn", "text": f"*Hata Kodu*: {self.err_code}"},
            },
        ]
