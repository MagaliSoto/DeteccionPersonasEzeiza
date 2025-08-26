import mysql.connector
from . import dbconfig

class DBManager:
    def __init__(self, nombre_tabla, estructura_tabla):
        """
        Inicializa la clase y crea la tabla si no existe.

        Parámetros:
            nombre_tabla (str): Nombre de la tabla.
            estructura_tabla (dict): Diccionario con formato {columna: tipo_sql}
                                     El usuario debe incluir 'ID' como clave primaria.
        """
        self.nombre_tabla = nombre_tabla
        self.estructura_tabla = estructura_tabla
        self.crear_tabla(nombre_tabla, estructura_tabla)

    def guardar_datos(self, track_id, datos_dict):
        """
        Inserta o actualiza dinámicamente columnas en la tabla especificada.

        Parámetros:
            track_id (int): Identificador único.
            datos_dict (dict): Diccionario con columnas y valores a guardar.
                               No debe incluir 'ID', se agrega automáticamente.
        """
        datos_dict = datos_dict.copy()
        datos_dict['ID'] = track_id

        columnas = ", ".join(f"`{k}`" for k in datos_dict.keys())
        placeholders = ", ".join(["%s"] * len(datos_dict))
        updates = ", ".join(f"`{k}` = VALUES(`{k}`)" for k in datos_dict if k != 'ID')

        sql = f"""
        INSERT INTO `{self.nombre_tabla}` ({columnas})
        VALUES ({placeholders})
        ON DUPLICATE KEY UPDATE {updates};
        """

        valores = tuple(datos_dict.values())
        self._ejecutar_sql(sql, valores, f"Guardar datos ID {track_id}")
    
    def obtener_datos(self, track_id=None):
        """
        Recupera datos de la tabla.

        Parámetros:
            track_id (int, opcional): Si se proporciona, filtra por ID.

        Retorna:
            list[dict]: Lista de filas como diccionarios.
        """
        try:
            conn = dbconfig.conectar()
            cursor = conn.cursor(dictionary=True)

            if track_id is not None:
                sql = f"SELECT * FROM `{self.nombre_tabla}` WHERE `ID` = %s;"
                cursor.execute(sql, (track_id,))
            else:
                sql = f"SELECT * FROM `{self.nombre_tabla}`;"
                cursor.execute(sql)

            resultados = cursor.fetchall()
            return resultados

        except mysql.connector.Error as err:
            print(f"[ERROR BD] Obtener datos: {err}")
            return []
        finally:
            if conn.is_connected():
                cursor.close()
                conn.close()
    
    def eliminar_datos(self, track_id):
        """
        Elimina una fila de la tabla según el ID proporcionado.

        Parámetros:
            track_id (int): Valor del ID a eliminar.
        """
        sql = f"DELETE FROM `{self.nombre_tabla}` WHERE `ID` = %s;"
        self._ejecutar_sql(sql, (track_id,), f"Eliminar datos ID {track_id}")

    def crear_tabla(self, nombre_tabla, columnas_dict):
        """
        Crea una tabla en la base de datos con el nombre y columnas proporcionadas.

        Parámetros:
            nombre_tabla (str): Nombre de la tabla a crear.
            columnas_dict (dict): Diccionario con los nombres de columnas como claves y los tipos SQL como valores.
        """
        if not columnas_dict:
            print("[ERROR BD] No se proporcionaron columnas para crear la tabla.")
            return

        columnas_sql = []
        for columna, tipo in columnas_dict.items():
            columnas_sql.append(f"`{columna}` {tipo}")

        columnas_def = ", ".join(columnas_sql)
        sql = f"CREATE TABLE IF NOT EXISTS `{nombre_tabla}` ({columnas_def});"
        self._ejecutar_sql(sql, (), f"Creación de tabla '{nombre_tabla}'")

    def _ejecutar_sql(self, sql, params, log_mensaje):
        """
        Ejecuta una consulta SQL de forma segura y gestiona la conexión a la base de datos.

        Parámetros:
            sql (str): Sentencia SQL a ejecutar.
            params (tuple): Parámetros para la consulta SQL.
            log_mensaje (str): Mensaje descriptivo para registrar en logs o consola.
        """
        try:
            conn = dbconfig.conectar()
            cursor = conn.cursor()
            cursor.execute(sql, params)
            conn.commit()
            #print(f"[BD] Éxito: {log_mensaje}")
        except mysql.connector.Error as err:
            print(f"[ERROR BD] {log_mensaje}: {err}")
        finally:
            if conn.is_connected():
                cursor.close()
                conn.close()