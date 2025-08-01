# Use nginx alpine image for lightweight static file serving
FROM nginx:alpine

# Remove default nginx website
RUN rm -rf /usr/share/nginx/html/*

# Copy the LOOPY app files to nginx html directory
COPY loopy/v1.1/ /usr/share/nginx/html/

# Create a custom nginx configuration if needed
# The default nginx configuration should work fine for static files
# But we can customize if needed

# Expose port 80
EXPOSE 80

# Start nginx
CMD ["nginx", "-g", "daemon off;"]