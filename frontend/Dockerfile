# Usamos Nginx Alpine
FROM nginx:alpine

# Copiamos los archivos de la app
COPY . /usr/share/nginx/html

# Copiamos la configuración de Nginx (proxy a /api/)
COPY nginx/default.conf /etc/nginx/conf.d/default.conf

# Exponemos el puerto 80
EXPOSE 80

# Arrancamos Nginx en primer plano
CMD ["nginx", "-g", "daemon off;"]
