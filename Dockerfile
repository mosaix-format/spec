FROM nginx:alpine
COPY site/ /usr/share/nginx/html/
COPY nginx-site.conf /etc/nginx/conf.d/default.conf
