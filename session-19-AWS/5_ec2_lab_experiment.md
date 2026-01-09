# AWS EC2 Hands-On Lab Experiment

## Experiment Overview

This hands-on lab provides a structured approach to implement and validate all concepts from the EC2 study guide. You'll build a complete distributed data processing system from scratch.

**Time Required**: 4-6 hours  
**Cost Estimate**: $5-10 (use Free Tier where possible)  
**Difficulty**: Intermediate

## Lab Architecture

You will build:
```
┌─────────────────────────────────────────────────┐
│              Your AWS Account                    │
│                                                  │
│  ┌────────────────────────────────────────┐    │
│  │           VPC (10.0.0.0/16)            │    │
│  │                                         │    │
│  │  ┌──────────────────────────────────┐  │    │
│  │  │   Public Subnet (10.0.1.0/24)    │  │    │
│  │  │                                   │  │    │
│  │  │  ┌─────────────────────────────┐ │  │    │
│  │  │  │   Master Node (t3.medium)   │ │  │    │
│  │  │  │   - Control plane           │ │  │    │
│  │  │  │   - Web UI access           │ │  │    │
│  │  │  │   - Public IP               │ │  │    │
│  │  │  └─────────────────────────────┘ │  │    │
│  │  │                                   │  │    │
│  │  │  ┌─────────────────────────────┐ │  │    │
│  │  │  │  Worker Node 1 (t3.small)   │ │  │    │
│  │  │  │   - Data processing         │ │  │    │
│  │  │  │   - Private IP only         │ │  │    │
│  │  │  └─────────────────────────────┘ │  │    │
│  │  │                                   │  │    │
│  │  │  ┌─────────────────────────────┐ │  │    │
│  │  │  │  Worker Node 2 (t3.small)   │ │  │    │
│  │  │  │   - Data processing         │ │  │    │
│  │  │  │   - Private IP only         │ │  │    │
│  │  │  └─────────────────────────────┘ │  │    │
│  │  │                                   │  │    │
│  │  └───────────────────────────────────┘  │    │
│  │                                         │    │
│  └─────────────────────────────────────────┘    │
│                                                  │
│  [S3 Bucket] - Shared storage                   │
│  [Elastic IP] - Static IP for master            │
│                                                  │
└──────────────────────────────────────────────────┘
```

## Prerequisites

### Required Tools
- AWS Account with billing enabled
- AWS CLI installed and configured
- SSH client (Terminal on Mac/Linux, PowerShell on Windows)
- Text editor (VS Code, Sublime, etc.)
- Basic knowledge of Linux commands

### AWS Free Tier Eligibility
- 750 hours of t2.micro/t3.micro per month
- 5 GB S3 storage
- Use t3.micro for workers if Free Tier eligible

## Lab Modules

The experiment is divided into 8 progressive modules, each building on the previous one.

---

# Module 1: Foundation Setup (30 minutes)

## Objectives
- Create and manage key pairs
- Understand AMI selection
- Launch your first EC2 instance
- Connect using multiple methods

## Tasks

### Task 1.1: Create Key Pair

```bash
# Set your region
export AWS_REGION=us-east-1

# Create key pair
aws ec2 create-key-pair \
  --key-name ec2-lab-key \
  --query 'KeyMaterial' \
  --output text > ec2-lab-key.pem

# Secure the key
chmod 400 ec2-lab-key.pem

# Verify key was created
aws ec2 describe-key-pairs --key-names ec2-lab-key
```

**Validation**: 
- Key file exists locally
- Permissions are 400 (read-only for owner)
- Key visible in AWS Console → EC2 → Key Pairs

### Task 1.2: Launch First Instance

```bash
# Find latest Amazon Linux 2023 AMI
AMI_ID=$(aws ec2 describe-images \
  --owners amazon \
  --filters "Name=name,Values=al2023-ami-2023.*-x86_64" \
  --query 'Images | sort_by(@, &CreationDate) | [-1].ImageId' \
  --output text)

echo "Using AMI: $AMI_ID"

# Create security group
SG_ID=$(aws ec2 create-security-group \
  --group-name ec2-lab-sg \
  --description "Security group for EC2 lab" \
  --output text)

echo "Security Group ID: $SG_ID"

# Allow SSH from your IP
MY_IP=$(curl -s https://checkip.amazonaws.com)
aws ec2 authorize-security-group-ingress \
  --group-id $SG_ID \
  --protocol tcp \
  --port 22 \
  --cidr ${MY_IP}/32

# Launch instance
INSTANCE_ID=$(aws ec2 run-instances \
  --image-id $AMI_ID \
  --instance-type t3.micro \
  --key-name ec2-lab-key \
  --security-group-ids $SG_ID \
  --tag-specifications 'ResourceType=instance,Tags=[{Key=Name,Value=Lab-Instance-1}]' \
  --query 'Instances[0].InstanceId' \
  --output text)

echo "Instance ID: $INSTANCE_ID"

# Wait for instance to be running
aws ec2 wait instance-running --instance-ids $INSTANCE_ID

# Get public IP
PUBLIC_IP=$(aws ec2 describe-instances \
  --instance-ids $INSTANCE_ID \
  --query 'Reservations[0].Instances[0].PublicIpAddress' \
  --output text)

echo "Public IP: $PUBLIC_IP"
```

**Validation**:
- Instance shows "running" in console
- Public IP assigned
- Security group allows SSH from your IP

### Task 1.3: Connect Using Multiple Methods

#### Method A: SSH Client
```bash
# Connect via SSH
ssh -i ec2-lab-key.pem ec2-user@$PUBLIC_IP

# Once connected, run these commands
whoami
hostname
pwd
ls -la
uname -a

# Exit
exit
```

#### Method B: EC2 Instance Connect (Console)
1. Go to AWS Console → EC2 → Instances
2. Select your instance
3. Click "Connect" → "EC2 Instance Connect"
4. Click "Connect"
5. Run same commands as above

#### Method C: Session Manager (SSM)
```bash
# First, attach IAM role to instance
# Create IAM role
aws iam create-role \
  --role-name EC2-SSM-Role \
  --assume-role-policy-document '{
    "Version": "2012-10-17",
    "Statement": [{
      "Effect": "Allow",
      "Principal": {"Service": "ec2.amazonaws.com"},
      "Action": "sts:AssumeRole"
    }]
  }'

# Attach SSM policy
aws iam attach-role-policy \
  --role-name EC2-SSM-Role \
  --policy-arn arn:aws:iam::aws:policy/AmazonSSMManagedInstanceCore

# Create instance profile
aws iam create-instance-profile \
  --instance-profile-name EC2-SSM-Profile

# Add role to instance profile
aws iam add-role-to-instance-profile \
  --instance-profile-name EC2-SSM-Profile \
  --role-name EC2-SSM-Role

# Wait 10 seconds for propagation
sleep 10

# Attach to instance
aws ec2 associate-iam-instance-profile \
  --instance-id $INSTANCE_ID \
  --iam-instance-profile Name=EC2-SSM-Profile

# Wait for SSM agent to register (2-3 minutes)
sleep 180

# Connect via Session Manager
aws ssm start-session --target $INSTANCE_ID
```

**Lab Questions**:
1. Which connection method required no security group rules?
2. Which method works without a key pair?
3. What's the trade-off between convenience and security?

**Expected Answers**:
1. Session Manager (SSM) - uses AWS Systems Manager
2. Both EC2 Instance Connect and Session Manager
3. SSH with key pairs offers most control but requires key management; Session Manager is most convenient but requires IAM setup

---

# Module 2: Instance Lifecycle Management (45 minutes)

## Objectives
- Understand instance states
- Practice stop/start/reboot/terminate
- Observe IP address changes
- Use Elastic IP for stable addressing

## Tasks

### Task 2.1: Explore Instance Lifecycle

```bash
# Get current state
aws ec2 describe-instances \
  --instance-ids $INSTANCE_ID \
  --query 'Reservations[0].Instances[0].State.Name' \
  --output text

# Record current public IP
echo "Original Public IP: $PUBLIC_IP"

# Stop instance
echo "Stopping instance..."
aws ec2 stop-instances --instance-ids $INSTANCE_ID
aws ec2 wait instance-stopped --instance-ids $INSTANCE_ID
echo "Instance stopped"

# Check state
aws ec2 describe-instances \
  --instance-ids $INSTANCE_ID \
  --query 'Reservations[0].Instances[0].State.Name'

# Start instance
echo "Starting instance..."
aws ec2 start-instances --instance-ids $INSTANCE_ID
aws ec2 wait instance-running --instance-ids $INSTANCE_ID
echo "Instance running"

# Get new public IP
NEW_PUBLIC_IP=$(aws ec2 describe-instances \
  --instance-ids $INSTANCE_ID \
  --query 'Reservations[0].Instances[0].PublicIpAddress' \
  --output text)

echo "Original IP: $PUBLIC_IP"
echo "New IP: $NEW_PUBLIC_IP"

# Compare
if [ "$PUBLIC_IP" != "$NEW_PUBLIC_IP" ]; then
  echo "✓ IP changed after stop/start (as expected)"
else
  echo "✗ IP did not change (unexpected)"
fi
```

**Validation**:
- Instance successfully stopped and started
- Public IP address changed
- Private IP address remained the same

### Task 2.2: Allocate and Attach Elastic IP

```bash
# Allocate Elastic IP
ALLOCATION_ID=$(aws ec2 allocate-address \
  --domain vpc \
  --query 'AllocationId' \
  --output text)

ELASTIC_IP=$(aws ec2 describe-addresses \
  --allocation-ids $ALLOCATION_ID \
  --query 'Addresses[0].PublicIp' \
  --output text)

echo "Allocated Elastic IP: $ELASTIC_IP"

# Associate with instance
ASSOCIATION_ID=$(aws ec2 associate-address \
  --instance-id $INSTANCE_ID \
  --allocation-id $ALLOCATION_ID \
  --query 'AssociationId' \
  --output text)

echo "Association ID: $ASSOCIATION_ID"

# Verify
CURRENT_IP=$(aws ec2 describe-instances \
  --instance-ids $INSTANCE_ID \
  --query 'Reservations[0].Instances[0].PublicIpAddress' \
  --output text)

echo "Current Public IP: $CURRENT_IP"
echo "Should match Elastic IP: $ELASTIC_IP"

# Test persistence: stop and start
aws ec2 stop-instances --instance-ids $INSTANCE_ID
aws ec2 wait instance-stopped --instance-ids $INSTANCE_ID
aws ec2 start-instances --instance-ids $INSTANCE_ID
aws ec2 wait instance-running --instance-ids $INSTANCE_ID

# Check IP again
AFTER_RESTART_IP=$(aws ec2 describe-instances \
  --instance-ids $INSTANCE_ID \
  --query 'Reservations[0].Instances[0].PublicIpAddress' \
  --output text)

echo "IP after restart: $AFTER_RESTART_IP"

if [ "$ELASTIC_IP" == "$AFTER_RESTART_IP" ]; then
  echo "✓ Elastic IP persisted through restart"
else
  echo "✗ Elastic IP did not persist"
fi
```

**Validation**:
- Elastic IP allocated successfully
- IP remains same after stop/start
- Can connect using Elastic IP

### Task 2.3: Reboot vs Stop/Start

```bash
# Create a test file to check data persistence
ssh -i ec2-lab-key.pem ec2-user@$ELASTIC_IP << 'EOF'
echo "Test data created at $(date)" > /home/ec2-user/test-file.txt
cat /home/ec2-user/test-file.txt
uptime
EOF

# Reboot
echo "Rebooting instance..."
aws ec2 reboot-instances --instance-ids $INSTANCE_ID
sleep 60  # Wait for reboot

# Check file still exists
ssh -i ec2-lab-key.pem ec2-user@$ELASTIC_IP << 'EOF'
echo "After reboot:"
cat /home/ec2-user/test-file.txt
uptime
EOF
```

**Lab Questions**:
1. What happened to the test file after reboot?
2. What happens to instance store data after stop/start?
3. When would you use reboot vs stop/start?

**Expected Answers**:
1. File persisted - EBS volumes survive reboots
2. Instance store data is lost after stop/start (not applicable to t3 instances)
3. Reboot for quick restart, stop/start to change instance type or save costs

---

# Module 3: Instance Types and Vertical Scaling (30 minutes)

## Objectives
- Change instance types
- Understand performance differences
- Practice vertical scaling

## Tasks

### Task 3.1: Benchmark Current Instance

```bash
# Connect and run CPU benchmark
ssh -i ec2-lab-key.pem ec2-user@$ELASTIC_IP << 'EOF'
# Install sysbench
sudo yum install -y sysbench

# Check current instance specs
echo "=== Current Instance Specs ==="
lscpu | grep "Model name"
lscpu | grep "CPU(s):"
free -h

# CPU benchmark
echo "=== CPU Benchmark ==="
sysbench cpu --cpu-max-prime=20000 --threads=1 run | grep "total time:"

# Save results
echo "t3.micro benchmark: $(sysbench cpu --cpu-max-prime=20000 --threads=1 run | grep 'total time:')" > benchmark-results.txt
EOF
```

### Task 3.2: Vertical Scale Up

```bash
# Stop instance
echo "Stopping instance for resize..."
aws ec2 stop-instances --instance-ids $INSTANCE_ID
aws ec2 wait instance-stopped --instance-ids $INSTANCE_ID

# Change instance type to t3.medium
echo "Changing to t3.medium..."
aws ec2 modify-instance-attribute \
  --instance-id $INSTANCE_ID \
  --instance-type "{\"Value\": \"t3.medium\"}"

# Start instance
echo "Starting resized instance..."
aws ec2 start-instances --instance-ids $INSTANCE_ID
aws ec2 wait instance-running --instance-ids $INSTANCE_ID

# Verify new instance type
NEW_TYPE=$(aws ec2 describe-instances \
  --instance-ids $INSTANCE_ID \
  --query 'Reservations[0].Instances[0].InstanceType' \
  --output text)

echo "New instance type: $NEW_TYPE"
```

### Task 3.3: Benchmark After Scaling

```bash
# Run benchmark on larger instance
ssh -i ec2-lab-key.pem ec2-user@$ELASTIC_IP << 'EOF'
echo "=== After Vertical Scaling ==="
lscpu | grep "Model name"
lscpu | grep "CPU(s):"
free -h

echo "=== CPU Benchmark ==="
sysbench cpu --cpu-max-prime=20000 --threads=2 run | grep "total time:"

# Append results
echo "t3.medium benchmark: $(sysbench cpu --cpu-max-prime=20000 --threads=2 run | grep 'total time:')" >> benchmark-results.txt

# Display comparison
cat benchmark-results.txt
EOF
```

**Lab Questions**:
1. How much did performance improve?
2. What was the downtime during scaling?
3. What are the limitations of vertical scaling?

**Expected Answers**:
1. Should see ~50-100% improvement (2 vCPU vs 1 vCPU)
2. Several minutes (time to stop, modify, start)
3. Limited by maximum instance size, requires downtime, single point of failure

---

# Module 4: Horizontal Scaling - Building a Cluster (60 minutes)

## Objectives
- Launch multiple instances
- Create a simple distributed system
- Understand cluster coordination
- Implement load distribution

## Tasks

### Task 4.1: Launch Worker Nodes

```bash
# Tag the current instance as Master
aws ec2 create-tags \
  --resources $INSTANCE_ID \
  --tags Key=Role,Value=Master

# Launch 2 worker nodes
WORKER1_ID=$(aws ec2 run-instances \
  --image-id $AMI_ID \
  --instance-type t3.small \
  --key-name ec2-lab-key \
  --security-group-ids $SG_ID \
  --iam-instance-profile Name=EC2-SSM-Profile \
  --tag-specifications 'ResourceType=instance,Tags=[{Key=Name,Value=Worker-1},{Key=Role,Value=Worker}]' \
  --query 'Instances[0].InstanceId' \
  --output text)

WORKER2_ID=$(aws ec2 run-instances \
  --image-id $AMI_ID \
  --instance-type t3.small \
  --key-name ec2-lab-key \
  --security-group-ids $SG_ID \
  --iam-instance-profile Name=EC2-SSM-Profile \
  --tag-specifications 'ResourceType=instance,Tags=[{Key=Name,Value=Worker-2},{Key=Role,Value=Worker}]' \
  --query 'Instances[0].InstanceId' \
  --output text)

echo "Worker 1 ID: $WORKER1_ID"
echo "Worker 2 ID: $WORKER2_ID"

# Wait for workers
aws ec2 wait instance-running --instance-ids $WORKER1_ID $WORKER2_ID

# Get private IPs
WORKER1_IP=$(aws ec2 describe-instances \
  --instance-ids $WORKER1_ID \
  --query 'Reservations[0].Instances[0].PrivateIpAddress' \
  --output text)

WORKER2_IP=$(aws ec2 describe-instances \
  --instance-ids $WORKER2_ID \
  --query 'Reservations[0].Instances[0].PrivateIpAddress' \
  --output text)

echo "Worker 1 Private IP: $WORKER1_IP"
echo "Worker 2 Private IP: $WORKER2_IP"
```

### Task 4.2: Configure Inter-Instance Communication

```bash
# Update security group to allow internal communication
aws ec2 authorize-security-group-ingress \
  --group-id $SG_ID \
  --protocol tcp \
  --port 0-65535 \
  --source-group $SG_ID

# Verify connectivity from master to workers
ssh -i ec2-lab-key.pem ec2-user@$ELASTIC_IP << EOF
ping -c 3 $WORKER1_IP
ping -c 3 $WORKER2_IP
EOF
```

### Task 4.3: Build Simple Distributed System

Create a simple distributed word count system:

```bash
# On master node, create coordinator script
ssh -i ec2-lab-key.pem ec2-user@$ELASTIC_IP << 'EOF'
# Create sample data
mkdir -p ~/cluster-lab
cd ~/cluster-lab

# Generate test data
cat > data.txt << 'DATAEOF'
hello world
hello hadoop
hello spark
big data processing
distributed systems
cloud computing
aws ec2 instances
horizontal scaling
vertical scaling
data engineering
DATAEOF

# Create master coordinator script
cat > master.sh << 'MASTEREOF'
#!/bin/bash
# Simple distributed word count coordinator

WORKERS=("WORKER1_IP_PLACEHOLDER" "WORKER2_IP_PLACEHOLDER")
DATA_FILE="data.txt"

echo "=== Distributed Word Count System ==="
echo "Master node coordinating work..."

# Split data for workers
split -n l/2 $DATA_FILE worker-data-

# Send work to workers
echo "Distributing work to ${#WORKERS[@]} workers..."

# Send to worker 1
scp -i ~/ec2-lab-key.pem -o StrictHostKeyChecking=no \
  worker-data-aa ec2-user@${WORKERS[0]}:/home/ec2-user/input.txt

# Send to worker 2
scp -i ~/ec2-lab-key.pem -o StrictHostKeyChecking=no \
  worker-data-ab ec2-user@${WORKERS[1]}:/home/ec2-user/input.txt

# Process on workers
for worker_ip in "${WORKERS[@]}"; do
  echo "Requesting processing from $worker_ip..."
  ssh -i ~/ec2-lab-key.pem -o StrictHostKeyChecking=no \
    ec2-user@$worker_ip 'bash /home/ec2-user/worker.sh' &
done

wait

# Collect results
echo "Collecting results..."
scp -i ~/ec2-lab-key.pem -o StrictHostKeyChecking=no \
  ec2-user@${WORKERS[0]}:/home/ec2-user/output.txt worker1-output.txt

scp -i ~/ec2-lab-key.pem -o StrictHostKeyChecking=no \
  ec2-user@${WORKERS[1]}:/home/ec2-user/output.txt worker2-output.txt

# Merge results
echo "Merging results..."
cat worker1-output.txt worker2-output.txt | \
  sort | \
  awk '{count[$1]+=$2} END {for(word in count) print word, count[word]}' | \
  sort -k2 -nr > final-results.txt

echo "=== Top 10 Words ==="
head -10 final-results.txt
MASTEREOF

chmod +x master.sh

# Replace placeholders
sed -i "s/WORKER1_IP_PLACEHOLDER/$WORKER1_IP/g" master.sh
sed -i "s/WORKER2_IP_PLACEHOLDER/$WORKER2_IP/g" master.sh

# Copy key for inter-node communication
cp ~/ec2-lab-key.pem ~/cluster-lab/
chmod 400 ~/cluster-lab/ec2-lab-key.pem
EOF
```

```bash
# Create worker script on both workers
for WORKER_ID in $WORKER1_ID $WORKER2_ID; do
  aws ssm start-session --target $WORKER_ID << 'EOF'
cat > /home/ec2-user/worker.sh << 'WORKEREOF'
#!/bin/bash
# Simple worker node processor

echo "Worker $(hostname) processing data..."

# Word count processing
cat /home/ec2-user/input.txt | \
  tr ' ' '\n' | \
  sort | \
  uniq -c | \
  awk '{print $2, $1}' > /home/ec2-user/output.txt

echo "Worker $(hostname) completed processing"
WORKEREOF

chmod +x /home/ec2-user/worker.sh
exit
EOF
done
```

### Task 4.4: Run Distributed Processing

```bash
# Execute on master
ssh -i ec2-lab-key.pem ec2-user@$ELASTIC_IP << 'EOF'
cd ~/cluster-lab
./master.sh
EOF
```

**Validation**:
- All workers receive and process data
- Master successfully collects results
- Final word count is accurate

**Lab Questions**:
1. What role does the master node play?
2. How is work distributed?
3. What happens if a worker fails?
4. How is this different from vertical scaling?

---

# Module 5: Storage and EBS Management (30 minutes)

## Objectives
- Attach additional EBS volumes
- Understand volume lifecycle
- Practice snapshot and restore

## Tasks

### Task 5.1: Create and Attach EBS Volume

```bash
# Create 8GB EBS volume
VOLUME_ID=$(aws ec2 create-volume \
  --availability-zone us-east-1a \
  --size 8 \
  --volume-type gp3 \
  --tag-specifications 'ResourceType=volume,Tags=[{Key=Name,Value=Lab-Data-Volume}]' \
  --query 'VolumeId' \
  --output text)

echo "Volume ID: $VOLUME_ID"

# Wait for available state
aws ec2 wait volume-available --volume-ids $VOLUME_ID

# Attach to master instance
aws ec2 attach-volume \
  --volume-id $VOLUME_ID \
  --instance-id $INSTANCE_ID \
  --device /dev/xvdf

# Wait for attachment
sleep 10

# Format and mount on instance
ssh -i ec2-lab-key.pem ec2-user@$ELASTIC_IP << 'EOF'
# Check new device
lsblk

# Format the volume
sudo mkfs -t ext4 /dev/xvdf

# Create mount point
sudo mkdir /data

# Mount the volume
sudo mount /dev/xvdf /data

# Change ownership
sudo chown ec2-user:ec2-user /data

# Verify
df -h | grep /data

# Create test data
echo "This data is on EBS volume" > /data/test.txt
cat /data/test.txt
EOF
```

### Task 5.2: Create Snapshot

```bash
# Create snapshot
SNAPSHOT_ID=$(aws ec2 create-snapshot \
  --volume-id $VOLUME_ID \
  --description "Lab data volume snapshot" \
  --tag-specifications 'ResourceType=snapshot,Tags=[{Key=Name,Value=Lab-Snapshot}]' \
  --query 'SnapshotId' \
  --output text)

echo "Snapshot ID: $SNAPSHOT_ID"

# Wait for completion
aws ec2 wait snapshot-completed --snapshot-ids $SNAPSHOT_ID

# Verify
aws ec2 describe-snapshots --snapshot-ids $SNAPSHOT_ID
```

### Task 5.3: Restore from Snapshot

```bash
# Create new volume from snapshot
NEW_VOLUME_ID=$(aws ec2 create-volume \
  --availability-zone us-east-1a \
  --snapshot-id $SNAPSHOT_ID \
  --tag-specifications 'ResourceType=volume,Tags=[{Key=Name,Value=Restored-Volume}]' \
  --query 'VolumeId' \
  --output text)

echo "Restored Volume ID: $NEW_VOLUME_ID"

# Wait and attach to worker
aws ec2 wait volume-available --volume-ids $NEW_VOLUME_ID

aws ec2 attach-volume \
  --volume-id $NEW_VOLUME_ID \
  --instance-id $WORKER1_ID \
  --device /dev/xvdf

# Mount and verify on worker
aws ssm start-session --target $WORKER1_ID << 'EOF'
sudo mkdir /restored-data
sudo mount /dev/xvdf /restored-data
cat /restored-data/test.txt
exit
EOF
```

**Validation**:
- Data accessible on new volume
- Snapshot successfully created and restored

---

# Module 6: Cost Monitoring and Optimization (20 minutes)

## Objectives
- Track instance costs
- Practice cost-saving techniques
- Understand billing impacts

## Tasks

### Task 6.1: Review Current Costs

```bash
# List all running instances with types
aws ec2 describe-instances \
  --filters "Name=instance-state-name,Values=running" \
  --query 'Reservations[*].Instances[*].[InstanceId,InstanceType,LaunchTime,Tags[?Key==`Name`].Value|[0]]' \
  --output table

# Calculate estimated hourly cost
echo "=== Estimated Hourly Costs (us-east-1) ==="
echo "t3.micro: ~\$0.0104/hour"
echo "t3.small: ~\$0.0208/hour"
echo "t3.medium: ~\$0.0416/hour"
echo ""
echo "Your cluster:"
echo "1x t3.medium (Master): \$0.0416/hour"
echo "2x t3.small (Workers): \$0.0416/hour"
echo "Total: ~\$0.0832/hour or ~\$2/day"
```

### Task 6.2: Implement Cost Savings

```bash
# Stop worker nodes when not in use
echo "Stopping worker nodes to save costs..."
aws ec2 stop-instances --instance-ids $WORKER1_ID $WORKER2_ID

# Check states
aws ec2 describe-instances \
  --instance-ids $WORKER1_ID $WORKER2_ID \
  --query 'Reservations[*].Instances[*].[InstanceId,State.Name]' \
  --output table

# Start only when needed
echo "Workers can be started on-demand with:"
echo "aws ec2 start-instances --instance-ids $WORKER1_ID $WORKER2_ID"
```

### Task 6.3: Review EBS Costs

```bash
# List all volumes
aws ec2 describe-volumes \
  --query 'Volumes[*].[VolumeId,Size,State,Tags[?Key==`Name`].Value|[0]]' \
  --output table

echo ""
echo "EBS gp3 pricing: ~\$0.08/GB-month"
echo "Your volumes: Total GB × \$0.08"
```

**Lab Questions**:
1. What costs continue even when instances are stopped?
2. How can you minimize costs in this lab?
3. What's the trade-off between always-on vs on-demand?

---

# Module 7: Security and Access Control (30 minutes)

## Objectives
- Configure security groups properly
- Understand the principle of least privilege
- Implement IAM roles

## Tasks

### Task 7.1: Review Security Group Rules

```bash
# Describe current security group
aws ec2 describe-security-groups \
  --group-ids $SG_ID \
  --query 'SecurityGroups[0].IpPermissions'

# Check for overly permissive rules
echo "Checking for security issues..."
aws ec2 describe-security-groups \
  --group-ids $SG_ID \
  --query 'SecurityGroups[0].IpPermissions[?IpRanges[?CidrIp==`0.0.0.0/0`]]'
```

### Task 7.2: Implement Least Privilege

```bash
# Remove overly broad access if any
# aws ec2 revoke-security-group-ingress \
#   --group-id $SG_ID \
#   --protocol tcp \
#   --port 22 \
#   --cidr 0.0.0.0/0

# Add specific IP access
MY_IP=$(curl -s https://checkip.amazonaws.com)
aws ec2 authorize-security-group-ingress \
  --group-id $SG_ID \
  --protocol tcp \
  --port 22 \
  --cidr ${MY_IP}/32

echo "SSH access limited to your IP: ${MY_IP}/32"
```

### Task 7.3: Create S3 Access Role

```bash
# Create role for S3 access
aws iam create-role \
  --role-name EC2-S3-Access-Role \
  --assume-role-policy-document '{
    "Version": "2012-10-17",
    "Statement": [{
      "Effect": "Allow",
      "Principal": {"Service": "ec2.amazonaws.com"},
      "Action": "sts:AssumeRole"
    }]
  }'

# Attach S3 read-only policy
aws iam attach-role-policy \
  --role-name EC2-S3-Access-Role \
  --policy-arn arn:aws:iam::aws:policy/AmazonS3ReadOnlyAccess

# Create instance profile
aws iam create-instance-profile \
  --instance-profile-name EC2-S3-Profile

aws iam add-role-to-instance-profile \
  --instance-profile-name EC2-S3-Profile \
  --role-name EC2-S3-Access-Role

# Attach to master instance
aws ec2 associate-iam-instance-profile \
  --instance-id $INSTANCE_ID \
  --iam-instance-profile Name=EC2-S3-Profile

# Test S3 access
ssh -i ec2-lab-key.pem ec2-user@$ELASTIC_IP << 'EOF'
aws s3 ls
echo "✓ Can list S3 buckets without credentials"
EOF
```

---

# Module 8: Monitoring and Troubleshooting (30 minutes)

## Objectives
- Monitor instance metrics
- Practice troubleshooting common issues
- Use CloudWatch for monitoring

## Tasks

### Task 8.1: Monitor Instance Metrics

```bash
# Get CPU utilization
aws cloudwatch get-metric-statistics \
  --namespace AWS/EC2 \
  --metric-name CPUUtilization \
  --dimensions Name=InstanceId,Value=$INSTANCE_ID \
  --start-time $(date -u -d '1 hour ago' +%Y-%m-%dT%H:%M:%S) \
  --end-time $(date -u +%Y-%m-%dT%H:%M:%S) \
  --period 300 \
  --statistics Average \
  --query 'Datapoints | sort_by(@, &Timestamp)' \
  --output table
```

### Task 8.2: Generate Load and Monitor

```bash
# Generate CPU load
ssh -i ec2-lab-key.pem ec2-user@$ELASTIC_IP << 'EOF'
echo "Generating CPU load for 2 minutes..."
yes > /dev/null &
LOAD_PID=$!
sleep 120
kill $LOAD_PID
echo "Load generation complete"
EOF

# Wait a moment for metrics
sleep 60

# Check metrics again
aws cloudwatch get-metric-statistics \
  --namespace AWS/EC2 \
  --metric-name CPUUtilization \
  --dimensions Name=InstanceId,Value=$INSTANCE_ID \
  --start-time $(date -u -d '5 minutes ago' +%Y-%m-%dT%H:%M:%S) \
  --end-time $(date -u +%Y-%m-%dT%H:%M:%S) \
  --period 60 \
  --statistics Average,Maximum \
  --query 'Datapoints | sort_by(@, &Timestamp)[-5:]' \
  --output table
```

### Task 8.3: Troubleshooting Exercise

```bash
# Simulate common issues and resolve them

echo "Exercise 1: Instance won't connect via SSH"
echo "Possible causes:"
echo "1. Security group doesn't allow SSH"
echo "2. Wrong key pair"
echo "3. Instance not running"
echo "4. Wrong username"

# Check security group
aws ec2 describe-security-groups \
  --group-ids $SG_ID \
  --query 'SecurityGroups[0].IpPermissions[?FromPort==`22`]'

# Check instance state
aws ec2 describe-instances \
  --instance-ids $INSTANCE_ID \
  --query 'Reservations[0].Instances[0].State'

# Check system logs if needed
aws ec2 get-console-output --instance-id $INSTANCE_ID
```

---

# Cleanup Procedure

**IMPORTANT**: Run this to avoid charges!

```bash
# Save instance IDs and other resources for reference
echo "Master Instance: $INSTANCE_ID"
echo "Worker 1: $WORKER1_ID"
echo "Worker 2: $WORKER2_ID"
echo "Security Group: $SG_ID"
echo "Elastic IP: $ALLOCATION_ID"
echo "EBS Volume: $VOLUME_ID"
echo "New Volume: $NEW_VOLUME_ID"
echo "Snapshot: $SNAPSHOT_ID"

# Step 1: Terminate all instances
echo "Terminating instances..."
aws ec2 terminate-instances \
  --instance-ids $INSTANCE_ID $WORKER1_ID $WORKER2_ID

# Wait for termination
aws ec2 wait instance-terminated \
  --instance-ids $INSTANCE_ID $WORKER1_ID $WORKER2_ID

# Step 2: Release Elastic IP
echo "Releasing Elastic IP..."
aws ec2 release-address --allocation-id $ALLOCATION_ID

# Step 3: Delete volumes (after detachment)
echo "Deleting volumes..."
sleep 30
aws ec2 delete-volume --volume-id $VOLUME_ID
aws ec2 delete-volume --volume-id $NEW_VOLUME_ID

# Step 4: Delete snapshot
echo "Deleting snapshot..."
aws ec2 delete-snapshot --snapshot-id $SNAPSHOT_ID

# Step 5: Delete security group
echo "Deleting security group..."
aws ec2 delete-security-group --group-id $SG_ID

# Step 6: Delete key pair
echo "Deleting key pair..."
aws ec2 delete-key-pair --key-name ec2-lab-key
rm -f ec2-lab-key.pem

# Step 7: Remove IAM roles and profiles
echo "Cleaning up IAM resources..."
aws iam remove-role-from-instance-profile \
  --instance-profile-name EC2-SSM-Profile \
  --role-name EC2-SSM-Role

aws iam delete-instance-profile \
  --instance-profile-name EC2-SSM-Profile

aws iam detach-role-policy \
  --role-name EC2-SSM-Role \
  --policy-arn arn:aws:iam::aws:policy/AmazonSSMManagedInstanceCore

aws iam delete-role --role-name EC2-SSM-Role

# Do the same for S3 access role
aws iam remove-role-from-instance-profile \
  --instance-profile-name EC2-S3-Profile \
  --role-name EC2-S3-Access-Role

aws iam delete-instance-profile \
  --instance-profile-name EC2-S3-Profile

aws iam detach-role-policy \
  --role-name EC2-S3-Access-Role \
  --policy-arn arn:aws:iam::aws:policy/AmazonS3ReadOnlyAccess

aws iam delete-role --role-name EC2-S3-Access-Role

echo "✓ Cleanup complete!"
```

---

# Lab Report Template

After completing the lab, document your findings:

```markdown
# EC2 Lab Experiment Report

## Student Information
- Name: [Your Name]
- Date: [Date]
- Time Spent: [Hours]

## Module 1: Foundation Setup
- Connection methods tested: [ ] SSH [ ] Instance Connect [ ] SSM
- Which method was easiest? Why?
- Issues encountered:

## Module 2: Instance Lifecycle
- Original IP: _______________
- IP after restart: _______________
- Elastic IP: _______________
- Did Elastic IP persist? Yes/No

## Module 3: Vertical Scaling
- t3.micro benchmark time: _______________
- t3.medium benchmark time: _______________
- Performance improvement: _______________%
- Downtime duration: _______________

## Module 4: Horizontal Scaling
- Number of workers launched: _______________
- Distributed processing successful? Yes/No
- What challenges did you face?
- How does this compare to vertical scaling?

## Module 5: Storage Management
- EBS volume created: _______________GB
- Snapshot created successfully? Yes/No
- Data restored correctly? Yes/No

## Module 6: Cost Analysis
- Estimated lab cost: $_______________
- Ways to reduce costs:
  1.
  2.
  3.

## Module 7: Security
- Security group properly configured? Yes/No
- IAM roles working correctly? Yes/No
- Principle of least privilege applied? Yes/No

## Module 8: Monitoring
- Peak CPU usage observed: _______________%
- CloudWatch metrics accessible? Yes/No
- Common issues identified:

## Key Learnings
1.
2.
3.

## Challenges Faced
1.
2.
3.

## Recommendations
What would you do differently next time?
```

---

# Advanced Extensions (Optional)

If you complete the main lab, try these challenges:

## Extension 1: Auto Scaling
- Create Launch Template
- Set up Auto Scaling Group
- Configure scaling policies
- Test automatic scaling

## Extension 2: Load Balancer
- Create Application Load Balancer
- Distribute traffic across workers
- Test health checks
- Implement sticky sessions

## Extension 3: Real Spark Cluster
- Install Apache Spark on all nodes
- Configure master and workers
- Run actual Spark jobs
- Process real datasets

## Extension 4: Monitoring Dashboard
- Create CloudWatch Dashboard
- Set up alarms
- Configure SNS notifications
- Monitor cluster health

## Extension 5: Infrastructure as Code
- Convert entire lab to CloudFormation
- Use Terraform instead
- Implement proper tagging
- Create reusable modules

---

# Troubleshooting Guide

## Common Issues and Solutions

### Issue: Cannot connect via SSH
**Symptoms**: Connection timeout or refused
**Solutions**:
1. Check security group allows port 22 from your IP
2. Verify instance is running
3. Confirm correct key pair and permissions (chmod 400)
4. Check username (ec2-user for Amazon Linux)

### Issue: Elastic IP costs
**Symptoms**: Unexpected charges
**Solutions**:
1. Elastic IPs are free when attached to running instance
2. Release unused Elastic IPs immediately
3. Only allocate when needed

### Issue: Instances won't communicate
**Symptoms**: Workers can't reach master
**Solutions**:
1. Verify security group allows internal traffic
2. Check VPC settings
3. Confirm instances in same subnet
4. Test with ping first

### Issue: EBS volume not appearing
**Symptoms**: lsblk doesn't show new device
**Solutions**:
1. Wait 30 seconds after attachment
2. Check attachment state in console
3. Verify correct device name
4. Reboot instance if necessary

### Issue: High costs
**Symptoms**: Bill higher than expected
**Solutions**:
1. Stop unused instances
2. Delete unattached volumes
3. Remove old snapshots
4. Release unused Elastic IPs
5. Check CloudWatch for idle resources

---

# Success Criteria

You have successfully completed this lab if you can:

✅ Launch and connect to EC2 instances using multiple methods  
✅ Manage instance lifecycle (stop, start, reboot, terminate)  
✅ Use Elastic IPs for stable addressing  
✅ Perform vertical scaling by changing instance types  
✅ Build a horizontal scaled cluster with master and workers  
✅ Create, attach, and manage EBS volumes  
✅ Take snapshots and restore from them  
✅ Configure security groups with least privilege  
✅ Implement IAM roles for service access  
✅ Monitor instances using CloudWatch  
✅ Clean up all resources to avoid charges  

---

# Assessment Questions

Test your understanding:

1. **When would you choose vertical scaling over horizontal scaling?**

2. **Explain the relationship between AMI, Instance, and Snapshot.**

3. **Why does a public IP change after stop/start, and how do you prevent this?**

4. **What resources continue to incur charges when an instance is stopped?**

5. **Describe the master-worker architecture and its benefits.**

6. **What's the difference between rebooting and stop/start?**

7. **Why is Session Manager (SSM) more secure than traditional SSH?**

8. **How would you handle a scenario where one worker fails in your cluster?**

9. **What's the purpose of security groups vs IAM roles?**

10. **Explain the complete lifecycle of an EC2 instance from launch to termination.**

---

# Additional Resources

- AWS EC2 User Guide: https://docs.aws.amazon.com/ec2/
- AWS CLI Command Reference: https://docs.aws.amazon.com/cli/
- AWS Free Tier: https://aws.amazon.com/free/
- EC2 Pricing: https://aws.amazon.com/ec2/pricing/
- CloudWatch Documentation: https://docs.aws.amazon.com/cloudwatch/

---

**End of Lab Experiment**

Remember to clean up all resources after completing the lab to avoid unnecessary charges!