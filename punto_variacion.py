class CaracteristicaConfiguracion:
    def __init__(self, caracteristica, estado, contenedorDocker, href):
        self._caracteristica = caracteristica
        self._estado = estado
        self._contenedorDocker = contenedorDocker
        self._subCaracteristicas = []
        self._href = href

    @property
    def getCaracteristica(self):
        return self._caracteristica

    @property
    def getEstado(self):
        return self._estado

    @property
    def getContenedorDocker(self):
        return self._contenedorDocker

    @property
    def getSubcaracteristicas(self):
        return self._subCaracteristicas

    def agregarRelacion(self, caracteristica):
        self._subCaracteristicas.append(caracteristica)

    @property
    def getHref(self):
        return self._href




class PuntoVariacion:
    def __init__(self, estadoConfiguracion, grafoMC, caracteristicaRaiz):
        self._modeloConfiguracion = self.agregarRelacionesCaracteristicas(self.agregarCaracteristicas(estadoConfiguracion),grafoMC, caracteristicaRaiz)
        self._grafoCaracteristicas = grafoMC

    def obtenerConfiguracion(self):
        reconfiguracion = {}
        for caracteristica in self._modeloConfiguracion:
            reconfiguracion.update({caracteristica.getCaracteristica.replace(" ","_").lower(): caracteristica.getEstado})
        return reconfiguracion

    def obtenerConfiguracionNivel(self,nombreCaracteristica):
        reconfiguracion = {"links" : []}
        for caracteristica in self._modeloConfiguracion:
            print(caracteristica.getCaracteristica)
            if caracteristica.getCaracteristica == nombreCaracteristica:
                for subCaracteristica in caracteristica.getSubcaracteristicas:
                    if subCaracteristica.getEstado:
                        configuracion = {}
                        configuracion.update({"name" : subCaracteristica.getCaracteristica.replace(" ","_").lower()})
                        configuracion.update({"href": subCaracteristica.getHref.replace(" ","_").lower()})
                        reconfiguracion["links"].append(configuracion)
                print(reconfiguracion)
                return reconfiguracion
        return None
    def obtenerEstadoCaracteristica(self, nombreCaracteristicas):
        reconfiguracion = {}
        for caracteristica in self._modeloConfiguracion:
            if caracteristica.getCaracteristica == nombreCaracteristicas:
                configuracion = {}
                if(caracteristica.getEstado):
                    reconfiguracion.update({"name": caracteristica.getCaracteristica.replace(" ","_").lower()})
                    reconfiguracion.update({"href": caracteristica.getHref.replace(" ","_").lower()})
                return reconfiguracion
        return reconfiguracion


    def agregarCaracteristicas(self,estadoConfiguracion):
        modeloConfiguracion = []
        for caracteristica in estadoConfiguracion:
            estado = False
            if " activada" in caracteristica:
                estado = True
                caracteristica = caracteristica.replace(" activada", "")
            else:
                caracteristica = caracteristica.replace(" desactivada", "")
            href = "/"+caracteristica.replace(" ","_")
            caracteristicaConfiguracion = CaracteristicaConfiguracion(caracteristica.replace(" ","_").lower(),estado,caracteristica.replace(" ","_").lower(),href.lower())
            modeloConfiguracion.append(caracteristicaConfiguracion)
        return modeloConfiguracion

    def agregarCaracteristicaRaiz(self, nombreCaracteristica, grafoMC):
        href = "/" + nombreCaracteristica.replace(" ", "_")
        caracteristicaConfiguracion = CaracteristicaConfiguracion(nombreCaracteristica.replace(" ","_").lower(), True, nombreCaracteristica.replace(" ","_").lower(), href.lower())
        return caracteristicaConfiguracion

    def agregarRelacionesCaracteristicas(self, modeloConfiguracion, grafoMC, caracteristicaRaiz):
        modeloConfiguracion.append(self.agregarCaracteristicaRaiz(caracteristicaRaiz,grafoMC))
        for caracteristicaConf in modeloConfiguracion:
            relacionesCaracteristica = grafoMC.obtenerRelacionesCaracteristicaConRestriccion(caracteristicaConf.getCaracteristica.replace("_"," ").capitalize())
            for relacion in relacionesCaracteristica:
                for subCaracteristicaConf in modeloConfiguracion:
                    relacionCaracteristica = relacion.replace(" ","_").lower()
                    if relacionCaracteristica == subCaracteristicaConf.getCaracteristica:
                        caracteristicaConf.agregarRelacion(subCaracteristicaConf)
        return modeloConfiguracion
