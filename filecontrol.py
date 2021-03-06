# ///////////////////////////////////////////////////////////////
#
# Hecho por: Jairo Antonio Melo Flórez
# Realizado con: Qt Designer y PySide6
# © 2021 Fundación Histórica Neogranadina
# V: 0.1.0-alpha
#
# filecontrol:
# módulo para leer y guardar las capturas de la cámara 
#
# ///////////////////////////////////////////////////////////////

import chdkptp.util as util
import multiprocessing as mp
from pathlib import Path
import os
import datetime
from db import wrap_imageWithElement

DIR = Path("../capturas")

class DescargarIMGS:

    def __init__(self, imgdata, nombre_proyecto, folio, dev) -> None:
        '''
        imgdata(bin) = datos binarios de la imagen capturada (jpg)
        nombre_proyecto(str) = nombre del proyecto
        dev(object) = objeto chdkptp.ChdkDevice()
        '''
        self.dev = dev  # necesario para comunicarse con los archivos remotos
        self.imgdata = imgdata
        self.nombre_proyecto = nombre_proyecto
        self.folio = folio

    def img_dir(self, tipo_img):
        '''
        crea un nombre único para cada captura
        TODO: comprobar errores de sincronización que lleven a que los dng no coincidan con los jpg
        
        img_dir = os.path.join(DIR, self.nombre_proyecto,
                               f"{tipo_img.upper()}")
        os.makedirs(img_dir, exist_ok=True)
        lista = os.listdir(img_dir)
        # print(lista)
        number_files = len(lista)
        # print(number_files)
        fpath = os.path.join(img_dir, f"IMG_{number_files + 1}.{tipo_img}")

        if os.path.exists(fpath):
            dup_name = fpath.split("/")[-1]
            nombre_file = dup_name.split(".")[0]
            serie = nombre_file.split("_")[1]
            # ¿Podría ser R - V?
            fpath = os.path.join(img_dir, f"IMG_{int(serie) + 1}.{tipo_img}")

        return fpath
        '''

        img_dir = os.path.join(DIR, self.nombre_proyecto,
                               f"{tipo_img.upper()}")
        os.makedirs(img_dir, exist_ok=True)
        
        return img_dir


    def descarga_jpg(self):
        '''
        crea imagen jpg a partir del binario (imgdata)
        '''
        jpg_path = os.path.join(self.img_dir('jpg'), f"{self.folio}.jpg")

        with open(jpg_path, 'wb') as fp:
            fp.write(self.imgdata)
            self.associateImageWithElement(self.nombre_proyecto, jpg_path, 'jpg')
            print(f"descargada img {jpg_path}")

    def descarga_dng(self):
        '''
        copia la imagen dng desde la memoria de la cámara
        '''
        img_path = self.dng_remoto()

        raw_img = self.dev.download_file(img_path)
        if img_path.endswith(".DNG"):
            dng_path = os.path.join(self.img_dir('dng'), f"{self.folio}.dng")

        if not os.path.exists(dng_path):
            with open(dng_path, "wb") as fp:
                fp.write(raw_img)
                self.associateImageWithElement(self.nombre_proyecto, dng_path, 'dng')
                print(f"descargada img {dng_path}")

        self.dev.delete_files(img_path)

    def imgs_camara(self, detailed=True):
        '''
        lista de archivos guardados en la cámara remota
        '''
        ruta_dirCam = self.dev.list_files()[-1:][0][:-1]
        rp = util.to_camerapath(ruta_dirCam)
        flist = self.dev._lua.call("con:listdir", rp, dirsonly=False,
                                   stat="*" if detailed else "/")

        return flist

    def dng_remoto(self):
        '''
        ruta a la última imagen tomada por la cámara
        '''
        flist = self.imgs_camara()
        ruta_dirCam = self.dev.list_files()[-1:][0][:-1]
        ruta_camara = util.to_camerapath(ruta_dirCam)

        for l in flist.values():
            listac = [f"{ruta_camara}/{v}" for k,
                      v in l.items() if k == 'name']

        return listac[-1]


    def associateImageWithElement(self, element_id, img_path, tipo_img):
        '''
        get the metadata of each image and associate it with the element
        and write it in database
        '''
        element_id = int(element_id)

        if tipo_img == 'jpg':
            lista = os.listdir(self.img_dir('jpg'))
            order = len(lista)
        elif tipo_img == 'dng':
            lista = os.listdir(self.img_dir('dng'))
            order = len(lista)

        size = os.path.getsize(img_path)

        mime_type = 'image/jpeg' if tipo_img == 'jpg' else 'image/x-adobe-dng'

        filename = os.path.basename(img_path)
        path = os.path.dirname(img_path)
        img_timestamp = datetime.datetime.now()
        img_modified_ts = datetime.datetime.now()
        img_metadata = "coming soon"

        #debug
        print(f"element_id: {element_id}")
        print(f"order: {order}")
        print(f"img_path: {img_path}")
        print(f"tipo_img: {tipo_img}")
        print(f"size: {size}")
        print(f"mime_type: {mime_type}")
        print(f"filename: {filename}")
        print(f"path: {path}")
        print(f"img_timestamp: {img_timestamp}")
        print(f"img_modified_ts: {img_modified_ts}")
        print(f"img_metadata: {img_metadata}")

        wrap_imageWithElement(element_id, order, size, mime_type, filename,
                                path, img_timestamp, img_modified_ts,
                                img_metadata)
        