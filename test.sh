#!/bin/zsh

autoload colors
colors

setopt shwordsplit


if [[ "$terminfo[colors]" -gt 8 ]]; then
    colors
fi
for COLOR in RED GREEN YELLOW BLUE MAGENTA CYAN BLACK WHITE; do
    eval $COLOR='$fg_no_bold[${(L)COLOR}]'
    eval BOLD_$COLOR='$fg_bold[${(L)COLOR}]'
done
eval RESET='$reset_color'


printEnd()
{
	echo "------- end ${YELLOW}$1${RESET}"
}
printStart()
{
	echo "----- start ${YELLOW}$1${RESET}"
}
printError()
{
	echo "${RED}error: $1${RESET}"
}



INTERPRETER=python3
SCRIPT=epubtoc.py

TESTS_FOLDER=tests

if [[ -z $1 ]]; then
	TEST_INPUT_FOLDERS=$(print $TESTS_FOLDER/test*)
else
	TEST_INPUT_FOLDERS=$TESTS_FOLDER/$1
fi



FAIL=0

for folder in $TEST_INPUT_FOLDERS; do

	folder_name=`basename $folder`

	input_XML=$folder/input.xml
	input_ARG=$folder/input.arg

	output_ERR=$folder/result.err
	output_OUT=$folder/result.out

	expected_RET=$folder/expected.\!\!\!
	expected_XML=$folder/expected.xml

	diff_XML=$folder/diff.xml

	TEST_FAIL=0

	if [[ -e "$input_ARG" ]]; then
		arg=`cat "$input_ARG" | sed "s|\@\.|$folder|"`
	fi

	printStart $folder_name

	# ---------- run script -------------
	if [[ -e $input_XML ]]; then
		$INTERPRETER $SCRIPT ${=arg} "$input_XML" "$output_OUT" 2> "$output_ERR"
	else
		$INTERPRETER $SCRIPT ${=arg} > "$output_OUT" 2> "$output_ERR"
	fi

	# ----------- compare return code ------------
	RET=$?

	if [[ -e " $expected_RET" ]]; then
		EXP_RET=`cat "$expected_RET"`
	else
		EXP_RET=0
	fi


	if [[ $EXP_RET != $RET ]]; then
		printError "expected ret code: $EXP_RET ret code: $RET"
		TEST_FAIL=1
		FAIL=1
	fi

	if [[ $RET != 0 || $EXP_RET != 0 ]]; then
		if [[ $TEST_FAIL == 0 ]]; then
			print "${GREEN}OK${RESET}"
		fi
		printEnd $folder_name
		continue
	fi




	# -------------------------------------
	java -jar ~/bin/jexamxml.jar "$output_OUT" "$expected_XML" "$diff_XML" xml_options > /dev/null

	if [[ $? != 0 ]]; then
		printError "xml is not identical"
		TEST_FAIL=1
		FAIL=1
	fi



	if [[ $TEST_FAIL == 0 ]]; then
		print "${GREEN}OK${RESET}"
	fi

	printEnd $folder_name

done


# ------------------------------------------------------------------------------
if [[ $FAIL == 0 ]]; then
	echo -e "\n${GREEN}SUCCESS${RESET}\n"
else
	echo -e "\n${BOLD_RED}FAIL${RESET}\n"
fi
