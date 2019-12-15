.data
string0:	.asciiz	" "
string1:	.asciiz	" "
string2:	.asciiz	" "
string3:	.asciiz	" "
.text
j	main
por2:
addi	$sp,$sp,-8
sw	$fp,0($sp)
sw	$ra,4($sp)
move	$fp,$sp
lw	$t0,8($fp)
mul	$t0,$t0,2
addi	$sp,$sp,-4
sw	$t0,0($sp)
L0:
lw	$t0,-4($fp)
move	$sp,$fp
lw	$fp,0($sp)
addi	$sp,$sp,4
lw	$ra,0($sp)
addi	$sp,$sp,4
move	$v0,$t0
jr	$ra
L1:
move	$sp,$fp
lw	$fp,0($sp)
addi	$sp,$sp,4
lw	$ra,0($sp)
addi	$sp,$sp,4
jr	$ra
entre2:
addi	$sp,$sp,-8
sw	$fp,0($sp)
sw	$ra,4($sp)
move	$fp,$sp
lw	$t0,8($fp)
div	$t0,$t0,2
addi	$sp,$sp,-4
sw	$t0,0($sp)
L2:
lw	$t0,-4($fp)
move	$sp,$fp
lw	$fp,0($sp)
addi	$sp,$sp,4
lw	$ra,0($sp)
addi	$sp,$sp,4
move	$v0,$t0
jr	$ra
L3:
move	$sp,$fp
lw	$fp,0($sp)
addi	$sp,$sp,4
lw	$ra,0($sp)
addi	$sp,$sp,4
jr	$ra
main:
addi	$sp,$sp,-8
sw	$fp,0($sp)
sw	$ra,4($sp)
move	$fp,$sp
addi	$sp,$sp,-4
li	$t9,6
sw	$t9,0($sp)
L4:
lw	$t0,-4($fp)
bgt	$t0,5,L6
j	L5
L6:
lw	$t0,-4($fp)
addi	$t0,$t0,5
sw	$t0,-4($fp)
L7:
L5:
lw	$t0,-4($fp)
addi	$t0,$t0,1
sw	$t0,-4($fp)
lw	$t0,-4($fp)
li	$v0,1
move	$a0,$t0
syscall
li	$v0,4
la	$a0,string0
syscall
lw	$t0,-4($fp)
addi	$sp,$sp,-4
sw	$t0,0($sp)
jal	por2
addi	$sp,$sp,4
move	$t0,$v0
sw	$t0,-4($fp)
lw	$t0,-4($fp)
li	$v0,1
move	$a0,$t0
syscall
li	$v0,4
la	$a0,string1
syscall
lw	$t0,-4($fp)
addi	$sp,$sp,-4
sw	$t0,0($sp)
jal	entre2
addi	$sp,$sp,4
move	$t0,$v0
sw	$t0,-4($fp)
lw	$t0,-4($fp)
li	$v0,1
move	$a0,$t0
syscall
li	$v0,4
la	$a0,string2
syscall
L8:
L10:
lw	$t0,-4($fp)
bgt	$t0,0,L11
j	L9
L11:
lw	$t0,-4($fp)
li	$v0,1
move	$a0,$t0
syscall
lw	$t0,-4($fp)
subi	$t0,$t0,1
sw	$t0,-4($fp)
li	$v0,4
la	$a0,string3
syscall
L12:
j	L10
L9:
