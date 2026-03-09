# Odoo 19 Community Custom Image
# Personal AI Employee - Gold Tier
FROM odoo:19.0

LABEL maintainer="Personal AI Employee Project"
LABEL description="Custom Odoo 19 image for AI Employee Gold Tier integration"
LABEL version="1.0"

# Set environment variables
COPY .env .env
ENV $(grep -v '^#' .env | xargs)

# Create directories for custom addons
RUN mkdir -p /mnt/extra-addons

# Set proper permissions
RUN chown -R odoo:odoo /mnt/extra-addons

# Expose Odoo port
EXPOSE 8069

# Health check
HEALTHCHECK --interval=30s --timeout=10s --start-period=40s --retries=3 \
    CMD curl -f http://localhost:8069/web/health || exit 1

# Run as odoo user
USER odoo

# Default command (inherited from base image)
CMD ["odoo"]
