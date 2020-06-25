# A template Makefile of test example 01

# Compiler configurations
CC = gcc
CFLAG = -g -O3 -std=c11
INC = -Icrc32

# Source and target files
OUTPUT_DIR = build
SRCS = main.cc crc32/crc32.cc
OBJS = $(patsubst %.cc, $(OUTPUT_DIR)/%.o, $(SRCS))
DEPS = $(patsubst %.cc, $(OUTPUT_DIR)/%.d, $(SRCS))
TARGET = $(OUTPUT_DIR)/debug.exe

# rules
$(OUTPUT_DIR)/%.o: %.c
	@echo "build objects"
	@$(CC) $(CFLAG) $(INC) -c $< -o $@ -MMD -MP -MF $(OUTPUT_DIR)/$*.d

# targets
all: $(TARGET)

$(TARGET): $(OBJS)
	@$(CC) $^ -o $@

# add pre-requestes
-include ${DEPS}

.PHONY: clean all

clean:
	@rm -rf $(OUTPUT_DIR)/*.o $(OUTPUT_DIR)/*.d $(TARGET)
# EOF
