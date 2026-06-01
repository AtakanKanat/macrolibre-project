from abc import ABC, abstractmethod
import pandas as pd

class BasePlugin(ABC):
    """
    SBF Terminal için Eklenti (Plugin) temel sınıfı.
    Yeni veri setleri eklerken bu sınıftan türetin.
    """

    @property
    @abstractmethod
    def name(self) -> str:
        """Eklentinin adı (Örn: 'OWID Energy Data')."""
        pass

    @abstractmethod
    def fetch_data(self) -> pd.DataFrame:
        """
        Gerekli veriyi indirip işleyerek bir pandas DataFrame döndürür.
        Zorunlu sütunlar: 'ISO' (3 harfli), 'Yıl' (int), ve yeni gösterge sütunları.
        Diğer ülkeleri veya boş satırları barındırmaması tercih edilir.
        """
        pass

    @abstractmethod
    def get_metadata(self) -> dict:
        """
        UI'da gösterilmek üzere metadata döndürür.
        Format:
        {
            'Gösterge Adı': {
                'tanim': 'Tanım...',
                'birim': 'Birim...',
                'metodoloji': 'Kaynak...'
            }
        }
        """
        pass
