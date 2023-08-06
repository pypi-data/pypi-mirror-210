#!/usr/bin/bash
# ------------------------------------------------------------------------------
# es7s/core (G1/legacy)
# (c) 2022-2023 A. Shavykin <0.delameter@gmail.com>
# -----------------------------------------------------------------------------
# shellcheck disable=SC2119,SC2016
# shellcheck source=../../data/es7s-shell-commons.sh
__E7SL() { local c="$(realpath "$(dirname "$(readlink -f "$0")")")" ; local l=\
"es7s-shell-commons.sh" ; local p=( "$ES7S_SHELL_COMMONS" "$HOME/.es7s/data/$l"
"$c/../$l" ); while [[ ! $(type -t __es7s_com) =~ ^fu ]];do [[ -f "${p[0]}" ]]\
&& source "${p[0]}"; p=("${p[@]:1}"); [[ "${#p[@]}" -gt 0 ]] && continue; echo\
'ERROR: es7s/commons is missing ($ES7S_SHELL_COMMONS)'; exit 57; done }; __E7SL
# ------------------------------------------------------------- loader v.3B ---


ruler() {
    # args: [force=] [no_color=]
    # if first arg is non-empty value, displays ruler even in normal mode
    local f_inactive="$(_cs8 $I8_GRAY)"
    local f_active="$(_cs 4 53)"$'\e'"[${ES7S_THEME_COLOR_SGR:-34}m"
    local f_active_hl="$(_cs 4 53 33)"
    local width=$(_ww) shift=1
    # shift is needed because first char should be marked as 1, not 0

    local logo="${_y}es7s|${f_inactive}"
    local sep10="╹" section="#''''╵''''"

    local i begin end output label
    local n=$((1 + width / 10))
    for (( i=0 ; i<n ; i++ )) ; do
        [[ $i -eq 1 ]] && { shift=0 ; logo="│$logo" ; }
        label=$(( i * 10 ))
        local f=$f_active
        if [[ $((i%10)) -eq 0 ]] ; then f=$f_active_hl ; fi
        if [[ $((i%40)) -eq 0 ]] ; then begin="$f${logo}${f_inactive}"
                                   else begin="$f${sep10}${label}${f_inactive}$(_s 1)"
        fi ;  if [[ $i -eq 21 ]] ; then begin="$f${sep10}$(squeeze 9 <<< "weeeeeeeeee")$f_inactive"
            elif [[ $i -eq 40 ]] ; then begin="$f${ES7S_OVERFLOW}eeees7s${logo::1}$f_inactive"
        fi
        end="${section:$(( $(_ccp <<< "$begin") + shift ))}" ;
        output+="$begin$end"

        if [[ $( _ccp <<< "$output" ) -ge $width ]] ; then
            [[ -n $no_color ]] && output="$(_dcu <<< "$output")"
            squeeze $width <<< "$output"
            break
        fi
    done
}

[[ $* =~ --help ]] && exit 0
[[ $# -gt 0 ]] && echo "No arguments allowed" && exit 2
ruler
