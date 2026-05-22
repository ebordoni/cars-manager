ARG BUILD_FROM
FROM $BUILD_FROM

# Install system dependencies
RUN apk add --no-cache \
    python3 \
    py3-pip \
    tzdata \
    libmagic

# Copy rootfs overlay
COPY rootfs /

# Install Python dependencies
RUN pip3 install --no-cache-dir \
    flask==3.1.0 \
    werkzeug==3.1.3 \
    python-magic==0.4.27

# Ensure run script is executable
RUN chmod a+x /etc/s6-overlay/s6-rc.d/cars-manager/run

CMD ["/init"]
