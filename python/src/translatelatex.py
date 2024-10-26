import re
import regex

class LaTeX2CalcEngine:
    """
    Contains:
    - dictionaries of LaTeX expressions and their translation
    - functions used to translate LaTeX expressions
    """
    
    def __init__(self, TI_on=True, SC_on=False):
        self.TI_on = TI_on
        self.SC_on = SC_on

        self.symbols = {
            #
            "astem": "°",
            "\\degree": "°",
            "\\deg": "°",
            "\\kertom": "·",
            "dfrac": "frac",
            "end": "enj",

            # junk
            "\\ ": "",
            "\n": "",
            "\t": "",
            " ": "",
            "‰": "\\left(1/1000\\right)",
            "‱": "\\left(1/1000000\\right)",
            "{,}": ",",
            "$$": "",
            "\\circ": "∘",
            "...": "",
            "\\ldots": "",
            "\\dots": "",

            # operators, abs, infinity
            "\\pm": "±",
            "\\mp": "∓",
            "\\times": "*ΦcrossΦ",
            "\\div": "/",
            "\\cdot": "*",
            "\\left|": "abs(",
            "\\right|": ")",
            "\\infty": "∞",

            # geometry
            "\\sphericalangle": "∢",
            "\\angle": "∠",
            "\\parallel": "∥",
            "\\nparallel": "∦",
            "\\mid": "∣",
            "\\sim": "~",
            "\\propto": "∝",

            # ≠, ≡, ≢ , ≈
            "\\neq": "≠",
            "\\equiv": "≡",
            "\\not\\equiv": "≢",
            "\\approx": "≈",
            "&=": "=",

            # vectors & average value | \bar{\text{i}}+\bar{\text{j}}+\bar{\text{k}} | 𝕚 𝕛 ӄ
            "\\bar{i}": "𝕚",
            "\\bar{\\text{i}}": "𝕚",
            "\\bar{j}": "𝕛",
            "\\bar{\\text{j}}": "𝕛",
            "\\bar{k}": "ӄ",
            "\\bar{\\text{k}}": "ӄ",

        #   "\\bar": "",
        #  "\\overline": "",

            # negation ¬
            "\\neg": "¬",

            # subset ⊂⊆
            "\\subset": "⊂",
            "\\subseteq": "⊆",

            # set
            "\\mathbb{N}": "ℕ",
            "\\mathbb{Z}": "ℤ",
            "\\mathbb{Q}": "ℚ",
            "\\mathbb{R}": "ℝ",
            "\\mathbb{C}": "ℂ",
            "\\mathbb{P}": "ℙ",
            "\\varnothing": "∅",

            # ∈
            "\\notin": "∉",
            "\\setminus": "\\",
            "\\backslash": "\\",

            # ∀ ∃
            "\\forall": "∀",
            "\\exists": "∃",

            # logic
            "\\and": "∧",
            "\\or": "∨",

            # ∩∪
            "\\cap": "∩",
            "\\cup": "∪",
        }

        self.greek_letters = {            
            '\\Alpha': 'Α',
            '\\Beta': 'Β',
            '\\Gamma': 'Γ',
            '\\Delta': 'Δ',
            '\\Epsilon': 'Ε',
            '\\Zeta': 'Ζ',
            '\\Eta': 'Η',
            '\\Theta': 'Θ',
            '\\Iota': 'Ι',
            '\\Kappa': 'Κ',
            '\\Lambda': 'Λ',
            '\\Mu': 'Μ',
            '\\Nu': 'Ν',
            '\\Xi': 'Ξ',
            '\\Omicron': 'Ο',
            '\\Pi': 'Π',
            '\\Rho': 'Ρ',
            '\\Sigma': 'Σ',
            '\\Tau': 'Τ',
            '\\Upsilon': 'Υ',
            '\\Phi': 'Φ',
            '\\Chi': 'Χ',
            '\\Psi': 'Ψ',
            '\\Omega': 'Ω',
            '\\alpha': 'α',
            '\\beta': 'β',
            '\\gamma': 'γ',
            '\\delta': 'δ',
            '\\epsilon': 'ε',
            '\\varepsilon': 'ε',
            '\\O': 'Otso Veisterä',
            '\\upsilon': 'υ',
            '\\zeta': 'ζ',
            '\\eta': 'η',
            '\\theta': 'θ',
            '\\iota': 'ι',
            '\\kappa': 'κ',
            '\\lambda': 'λ',
            '\\mu': 'μ',
            '\\nu': 'ν',
            '\\xi': 'ξ',
            '\\omicron': 'ο',
            '\\pi': 'π',
            '\\rho': 'ρ',
            '\\sigma': 'σ',
            '\\tau': 'τ',
            '\\phi': 'φ',
            '\\varphi': 'φ',
            '\\chi': 'χ',
            '\\psi': 'ψ',
            '\\omega': 'ω',

            # extra
            '\\partial': '∂',
            '\\nabla': '∇'
            }

        self.constantsDict = {
            '6.67430*10^{−11}\\text{Nm}^2/\\text{kg}^2': '(_Gc)',
            'γ': '(_Gc)',
            'c_0': '(_c)',
            'R_{∞}': '(_Rdb)',
            '{R}_{∞}': '(_Rdb)',
            '{{R}_{∞}}': '(_Rdb)',
            'R_{\\text{H}}': '(1.0967758*10^7*(1/_m))',
            'R_H': '(1.0967758*10^7*(1/_m))',
            'g_n': '(Ｇ)',
            'g_{\\text{n}}': '(Ｇ)',
            'T_n': '(293.15_°K)',
            'p_0': '(101325_Pa)',
            'N_A': '(_Na)',
            'N_{\\text{A}}': '(_Na)',
            'V_m': '(_Vm)',
            'V_{\\text{m}}': '(_Vm)',
            # 'k': '(_k)', Käännös myöhemmin
            'm_e': '(_Me)',
            'm_{\\text{e}}': '(_Me)',
            'm_p': '(_Mp)',
            'm_{\\text{p}}': '(_Mp)',
            'm_n': '(_Mn)',
            'm_{\\text{n}}': '(_Mn)',
            'm_{\\text{d}}': '(3.3435838*10^{−24}*_g)',
            'm_{α}': '(6.644657*10^{−24}*_g)',
            'ε_0': '(_ε0)',
            'F': '(_Fc)',
            '\\hbar': '(%`´%)/(2*π)',
            'σ': '(_σ)'
        }

        # prefixes (4)
        self.SC_prefixes = {
            'y': 'yocto',
            'z': 'zepto',
            'a': 'atto',
            'f': 'femto',
            'p': 'pico',
            'n': 'nano',
            'µ': 'micro',
            'm': 'milli',
            'c': 'centi',
            'd': 'deci',
            'da': 'deca',
            'h': 'hecto',
            'k': 'kilo',
            'M': 'mega',
            'G': 'giga',
            'T': 'tera',
            'P': 'peta',
            'E': 'exa',
            'Z': 'zetta',
            'Y': 'yotta'
            }

        # units (5)
        self.SC_units = {
            'h': 'hour',
            'g': 'gram',
            'm': 'meter',
            's': 'second',
            'A': 'ampere',
            'K': 'kelvin',
            'mol': 'mole',
            'cd': 'candela',
            'rad': 'radian',
            'sr': 'steradian',
            'Hz': 'hertz',
            'N': 'newton',
            'Pa': 'pascal',
            'J': 'joule',
            'W': 'watt',
            'C': 'coulomb',
            'V': 'volt',
            'F': 'farad',
            'Ω': 'ohm',
            'S': 'siemens',
            'Wb': 'weber',
            'T': 'tesla',
            'H': 'henry',
            'lm': 'lumen',
            'lx': 'lux',
            'Bq': 'becquerel',
            'Gy': 'gray',
            'Sv': 'sievert'
            }

        self.prefixes = {
            'y': '10^{-24}',
            'z': '10^{-21}',
            'a': '10^{-18}',
            'f': '10^{-15}',
            'p': '10^{-12}',
            'n': '10^{-9}',
            'µ': '10^{-6}',
            'm': '10^{-3}',
            'c': '10^{-2}',
            'd': '10^{-1}',
            'da': '10^1',
            'h': '10^2',
            'k': '10^3',
            'M': '10^6',
            'G': '10^9',
            'T': '10^{12}',
            'P': '10^{15}',
            'E': '10^{18}',
            'Z': '10^{21}',
            'Y': '10^{24}' 
                }
        self.units = {
            'h': '´´´´r', # hr
            'g': '````m', # gm
            'l': 'l',
            'm': 'm',
            's': 's',
            'A': 'A',
            'mol': 'mol',
            'cd': 'cd',
            # 'rad': '@r',
            'sr': 'sr',
            'Hz': 'Hz',
            'N': 'N',
            'Pa': 'Pa',
            'J': 'J',
            'W': 'W',
            'C': 'coul',
            'V': 'V',
            'F': 'F',
            'Ω': 'Ω',
            'S': 'S',
            'Wb': 'Wb',
            'T': 'T',
            'H': 'henry',
            'lm': 'lm',
            'lx': 'lx',
            'Bq': 'BQ',
            'Gy': 'Gy',
            'Sv': 'Sv'
            }

        # fixlist (6)
        self.fixlist = [
            ",",
            ".",
            ";",
            ":",
            "∑",
            "∏",
            "∫",
            "sqrt",
            "root",
            "left",
            "right",
            "frac",
            "ln",
            "lg",
            "lb",
            "log",
            "int",
            "lim",
            "system",
            "abs",
            "sinh",
            "cosh",
            "tanh",
            "csch",
            "sech",
            "coth",
            "arcsinh",
            "arccosh",
            "arctanh",
            "arccsch",
            "arcsech",
            "arccoth",
            "sin",
            "cos",
            "tan",
            "csc",
            "sec",
            "cot",
            "arcsin",
            "arccos",
            "arctan",
            "arccsc",
            "arcsec",
            "arccot",
            "exp",
            "floor",
            "ceil",
            "sign",
            "round",
            "int",
            "arc",
            "nPr",
            "nCr",
            "dotP",
            "crossP"
        ]

        self.common_functions = [
            "sin",
            "cos",
            "tan",
            "csc",
            "sec",
            "cot",
            "arcsin",
            "arccos",
            "arctan",
            "arccsc",
            "arcsec",
            "arccot",
            "exp",
            "ln",
            "floor",
            "ceil",
            "sign",
            "round",
            "int"
        ]

        self.arrows = {
            "\\leftarrow": "←",
            "\\rightarrow": "→",
            "\\leftrightarrow": "↔",
            "\\Leftarrow": "⇐",
            "\\Rightarrow": "⇒",
            "\\Leftrightarrow": "⇔",
        }

    ###################################################################

    def translateSymbols(self, expression: str, dictionary: dict=None):
        if dictionary is None:
            dictionary = self.symbols
        for key, value in dictionary.items():
            expression = expression.replace(key, value)
        return expression

    def translateGreekLetters(self, expression: str, dictionary: dict=None):
        if dictionary is None:
            dictionary = self.greek_letters
        for key, value in dictionary.items():
            expression = expression.replace(key, value)
        return expression

    def translateArrows(self, expression: str, dictionary: dict=None):
        if not "arrow" in expression:
            return expression
        if dictionary is None:
            dictionary = self.arrows
        for latex, translation in dictionary.items():
            expression = expression.replace(latex, translation)
        return expression

    def applyTags(self, expression):
        # 1. ()
        old_expression = expression
        expression = "("+ expression + ")"
        result = regex.search(r'(?<rec>\((?:[^()]++|(?&rec))*\))', expression, flags=regex.VERBOSE)
        expression = old_expression
        if result:
            matches = result.captures('rec')
            matches.sort(key=len, reverse=True)
            copy_list = []
            for index, match in enumerate(matches):
                copy_list.append(match)
                tag = "$" + str(index) + "$"
                amount = copy_list.count(match)
                expression = expression.replace(match, "###", amount-1)
                expression = expression.replace(match, tag + match + tag, 1)
                expression = expression.replace("###", match, amount-1)

        # 2. {}
        old_expression = expression
        expression = "{"+ expression + "}"
        result = regex.search(r'(?<rec>\{(?:[^{}]++|(?&rec))*\})', expression, flags=regex.VERBOSE)
        expression = old_expression
        if result:
            matches = result.captures('rec')
            matches.sort(key=len, reverse=True)    #{x}{x}{x}{x+1}{x}{x+1}
            copy_list = []
            for index, match in enumerate(matches):
                copy_list.append(match)
                tag = "£" + str(index) + "£"
                amount = copy_list.count(match)
                expression = expression.replace(match, "###", amount-1)
                expression = expression.replace(match, tag + match + tag, 1)
                expression = expression.replace("###", match, amount-1)
        # 3. []
        old_expression = expression
        expression = "["+ expression + "]"
        result = regex.search(r'(?<rec>\[(?:[^\[\]]++|(?&rec))*\])', expression, flags=regex.VERBOSE)
        expression = old_expression
        if result:
            matches = result.captures('rec')
            matches.sort(key=len, reverse=True)
            copy_list = []
            for index, match in enumerate(matches):
                copy_list.append(match)
                tag = "`" + str(index) + "`"
                amount = copy_list.count(match)
                expression = expression.replace(match, "###", amount-1)
                expression = expression.replace(match, tag + match + tag, 1)
                expression = expression.replace("###", match, amount-1)
        return expression
  
    def translateConstants(self, expression: str, dictionary: dict=None):
        if dictionary is None:
            dictionary = self.constantsDict
        for constant, TIconstant in dictionary.items():
            TIconstant = TIconstant.replace("_", "⁃")
            expression = expression.replace(constant, TIconstant)
        
        expression = expression.replace("⁃Rdb", "~¤~").replace('R', '⁃Rc').replace("~¤~", "⁃Rdb")
        return expression

    def translateUnits1(self, expression):
        if not ("\\mathrm" in expression or "\\text" in expression):
            return expression
        for i in range(expression.count("\\mathrm")):
            match = re.search(r'\\mathrm\£(\d+)\£\{(.+)\}\£\1\£', expression)
            if match:
                tag = "£" + match.group(1) + "£" # \mathrm{\sin \left(3\ \frac{\text{kJ}}{\text{kg}\cdot \text{K}}\right)}-\mathrm{\text{kJ}}
                text_containing_units = match.group(2)
                if self.TI_on:
                    old_text_containing_units = text_containing_units
                    text_containing_units = re.sub(r'\\text\£(\d+)\£\{(.+)\}\£\1\£', r'\2', text_containing_units)
                    text_containing_units = re.sub(r'([\Ω°a-zA-Z]+)', r'⁃\1』', text_containing_units)
                    text_containing_units = text_containing_units.replace("\\⁃", "\\")
                    expression = expression.replace("\\mathrm" + tag + "{" + old_text_containing_units + "}" + tag, text_containing_units, 1)
                    expression = expression.replace("⁃K", "⁃°K")
                    for fix in self.fixlist:
                        expression = expression.replace(fix + "』", fix)
                
                elif self.SC_on:
                    # laitetaan mathrm sisällä oleviin yksikköihin text{} ja kääntö jatkuu seuraavassa osiossa
                    old_text_containing_units = text_containing_units
                    text_containing_units = re.sub(r'\\text\£(\d+)\£\{(.+)\}\£\1\£', r'\2', text_containing_units) # \mathrm{\text{}}
                    text_containing_units = re.sub(r'([\Ω°a-zA-Z]+)', r'\\text{\1}', text_containing_units)
                    expression = expression.replace("\\mathrm" + tag + "{" + old_text_containing_units + "}" + tag, text_containing_units, 1)
                    
                else:
                    old_text_containing_units = text_containing_units
                    expression = expression.replace("\\mathrm" + tag + "{" + old_text_containing_units + "}" + tag, text_containing_units, 1)
   

        for i in range(expression.count("\\text")):
            match = re.search(r'\\text\£(\d+)\£\{(.+)\}\£\1\£', expression)    
            if match:
                tag = "£" + match.group(1) + "£"
                unit = match.group(2)
                if self.TI_on:
                #    expression = expression.replace("\\text" + tag + "{K}" + tag, "(_°K)")
                        if unit == "C":
                            expression = expression.replace("°\\text" + tag + "{" + unit + "}" + tag, "⁃°" + unit).replace("\\text" + tag + "{" + unit + "}" + tag, "⁃" + unit)
                        elif unit == "K":                                                   # unit bullet hyphon \u2043
                            expression = expression.replace("\\text" + tag + "{" + unit + "}" + tag, "⁃°" + unit + "』")
                        else:
                            expression = expression.replace("\\text" + tag + "{" + unit + "}" + tag, "⁃" + unit + "』")

                elif self.SC_on:
                    # units with prefixes (prefixes (4))
                    global prefixes, units

                    hit = False
                    for prefix, full_prefix in self.SC_prefixes.items():
                        for unitIter, full_unit in self.SC_units.items():
                            if "\\text" + tag + "{" + prefix + unitIter + "}" + tag in expression:
                                expression = expression.replace("\\text" + tag + "{" + prefix + unitIter + "}" + tag, "(" + full_prefix + " " + full_unit + ")")
                                hit = True

                    # units (5)
                    for unitIter, full_unit in self.SC_units.items():
                        if "\\text" + tag + "{" + unitIter + "}" + tag in expression:
                            expression = expression.replace("\\text" + tag + "{" + unitIter + "}" + tag, full_unit)
                            hit = True
                    
                    if not hit:
                        expression = expression.replace("\\text" + tag + "{" + unit + "}" + tag, unit)


                else:
                    expression = expression.replace("\\text" + tag + "{" + unit + "}" + tag, unit)
            
            if self.SC_on:
                match = re.search(r'\\text\{(.+)\}', expression)  
                if match:
                    for prefix, full_prefix in self.SC_prefixes.items():
                        for unit, full_unit in self.SC_units.items():
                            if "\\text{" + prefix + unit + "}" in expression:
                                expression = expression.replace("\\text{" + prefix + unit + "}", "(" + full_prefix + " " + full_unit + ")")

                    # units (5)
                    for unit, full_unit in self.SC_units.items():
                        if "\\text{" + unit + "}" in expression:
                            expression = expression.replace("\\text{" + unit + "}", full_unit)

        for fix in self.fixlist:
            if "⁃" + fix in expression:
                expression = expression.replace("⁃" + fix + "』", fix)

        return expression

    def translateUnits2(self, expression):
        if "⁃" not in expression:
            return expression
        if self.TI_on:
            long_units = re.findall(r'⁃([°a-zA-Z\ΩÅ]+)', expression)
            for long_unit in long_units:
                if len(long_unit) > 1:
                    for unit, full_unit in self.units.items():
                        for prefix, full_prefix in self.prefixes.items():
                            if long_unit == "kgm":
                                expression = expression.replace("⁃" + long_unit, "(10^3*_gm*_m)", 1)
                            elif long_unit == "Nm":
                                expression = expression.replace("⁃" + long_unit, "(_N*_m)", 1)
                            elif long_unit == "Mx":
                                expression = expression.replace("⁃" + long_unit, "(10^(-8)_Wb)")
                            elif long_unit == "rad":
                                expression = expression.replace("⁃" + long_unit, "@r")
                            elif long_unit == prefix + unit:
                                expression = expression.replace("⁃" + long_unit, "(" + full_prefix + "*_"+ full_unit + ")", 1)
                            
                else:
                    for unit, full_unit in self.units.items():
                        if long_unit == "t":
                            expression = expression.replace("⁃" + long_unit, "(10^6*_gm)", 1)
                        elif long_unit == "G":
                            expression = expression.replace("⁃" + long_unit, "(10^(-4)*_T)")
                        elif long_unit == "Å":
                            expression = expression.replace("⁃" + long_unit, "(10^(-10)*_m)", 1)
                        elif long_unit == "M":
                            expression = expression.replace("⁃" + long_unit, "((_mol)/(_l))", 1)
                        elif long_unit == unit:
                            expression = expression.replace("⁃" + long_unit, "(_" + full_unit + ")", 1)
        
        return expression


# \cos ^{10}\frac{\sin ^{\sin ^{-2}\pi ^{\cos ^2\left(2\sin \pi \cos \pi \right)^{3\sec 1^2}}}3\pi ^{\sin ^{\frac{3}{4}}1}}{\frac{\pi }{4}}^{\frac{1}{2}}-\cos ^2\frac{3\pi }{4}^5

    def translateCommonFunctions(self, expression):
        common_funcs = [
            "floor",
            "ceil",
            "sign",
            "round",
            "int"
            ]
        
        for func in common_funcs:
            expression = expression.replace(func, f"\\{func}")

        for func in self.common_functions:
            for i in range(expression.count(f'\\{func}')):     

                expression = re.sub(
                        r'\\' + func + r'\^\£([0-9]+)\£\{(.+)\}\£\1\£\\frac\£([0-9]+)\£\{(.+)\}\£\3\£\£([0-9]+)\£\{(.+)\}\£\5\£',
                        r'\\' + func + r'^£\1£{\2}£\1£\\left$0\3$(((\4)/(\6))\\right)$0\3$',
                        expression
                    )
                
                expression = re.sub(
                        r'\\' + func + r'\^([α-ωΑ-Ωa-zA-Z0-9])\\frac\£([0-9]+)\£\{(.+)\}\£\2\£\£([0-9]+)\£\{(.+)\}\£\4\£',
                        r'\\' + func + r'^\1\\left$0\2$(((\3)/(\5))\\right)$0\2$',
                        expression
                    )

                if f'\\{func}\\frac' in expression:
                    expression = re.sub(
                        r'\\' + func + r'\\frac\£([0-9]+)\£\{(.+)\}\£\1\£\£([0-9]+)\£\{(.+)\}\£\3\£',
                        r'\\' + func + r'\\left$0\1$(((\2)/(\4))\\right)$0\1$',
                        expression
                    )
                
                ##############################################

                # \sin ^{2n}\left(x\right)
                expression = re.sub(
                    r'\\' + func + r'\^\£([0-9]+)\£\{(.+)\}\£\1\£\\left\$([0-9]+)\$\((.+)\\right\)\$\3\$\^\£([0-9]+)\£\{(.+)\}\£\5\£',
                    r'\(' + func + r'\(\4\^\(\6\)\)\)\^\(\2\)',
                    expression
                    )

                expression = re.sub(
                    r'\\' + func + r'\^\£([0-9]+)\£\{(.+)\}\£\1\£\\left\$([0-9]+)\$\((.+)\\right\)\$\3\$\^([α-ωΑ-Ωa-zA-Z0-9])',
                    r'\(' + func + r'\(\4\^\(\5\)\)\)\^\(\2\)',
                    expression
                    )

                # \sin ^2\left(x\right)
                expression = re.sub(
                    r'\\' + func + r'\^([α-ωΑ-Ωa-zA-Z0-9])\\left\$([0-9]+)\$\((.+)\\right\)\$\2\$\^\£([0-9]+)\£\{(.+)\}\£\4\£',
                    r'\(' + func + r'\(\3\^\(\5\)\)\)\^\(\1\)',
                    expression
                    )
                
                expression = re.sub(
                    r'\\' + func + r'\^([α-ωΑ-Ωa-zA-Z0-9])\\left\$([0-9]+)\$\((.+)\\right\)\$\2\$\^([α-ωΑ-Ωa-zA-Z0-9])',
                    r'\(' + func + r'\(\3\^\(\4\)\)\)\^\(\1\)',
                    expression
                    )

                ##############################################

                expression = re.sub(
                    r'\\' + func + r'\^\£([0-9]+)\£\{(.+)\}\£\1\£\\left\$([0-9]+)\$\((.+)\\right\)\$\3\$',
                    r'\(' + func + r'\(\4\)\)\^\(\2\)',
                    expression
                    )

                # \sin ^2\left(x\right)
                expression = re.sub(
                    r'\\' + func + r'\^([α-ωΑ-Ωa-zA-Z0-9])\\left\$([0-9]+)\$\((.+)\\right\)\$\2\$',
                    r'\(' + func + r'\(\3\)\)\^\(\1\)',
                    expression
                    )

                # \sin ^{2n}x^{2k}
                expression = re.sub(
                    r'\\' + func + r'\^\£([0-9]+)\£\{(.+)\}\£\1\£([\;\:\.\,α-ωΑ-Ωa-zA-Z0-9°]+)\^\£([0-9]+)\£\{(.+)\}\£\4\£',
                    r'\(' + func + r'\(\3\^\(\5\)\)\)\^\(\2\)',
                    expression
                    )
                
                # \sin ^{2n}x^2
                expression = re.sub(
                    r'\\' + func + r'\^\£([0-9]+)\£\{(.+)\}\£\1\£([\;\:\.\,α-ωΑ-Ωa-zA-Z0-9°]+)\^([α-ωΑ-Ωa-zA-Z0-9])',
                    r'\(' + func + r'\(\3\^\(\4\)\)\)\^\(\2\)',
                    expression
                    )

                # \sin ^2x^{2k}
                expression = re.sub(
                    r'\\' + func + r'\^([α-ωΑ-Ωa-zA-Z0-9])([\;\:\.\,α-ωΑ-Ωa-zA-Z0-9°]+)\^\£([0-9]+)\£\{(.+)\}\£\3\£',
                    r'\(' + func + r'\(\2\^\(\4\)\)\)\^\(\1\)',
                    expression
                    ) # korjaa
                
                # \sin ^{2n}x
                expression = re.sub(
                    r'\\' + func + r'\^\£([0-9]+)\£\{(.+)\}\£\1\£([\;\:\.\,α-ωΑ-Ωa-zA-Z0-9°]+)',
                    r'\(' + func + r'\(\3\)\)\^\(\2\)',
                    expression
                    )
                
                # \sin ^2x
                expression = re.sub(
                    r'\\' + func + r'\^([α-ωΑ-Ωa-zA-Z0-9])([\;\:\.\,α-ωΑ-Ωa-zA-Z0-9°]+)',
                    r'\(' + func + r'\(\2\)\)\^\(\1\)',
                    expression
                    )

                match = re.search(r'\\' + func + r'\\left\$([0-9]+)\$\((.+)\\right\)\$\1\$', expression)
                if match:
                    tag = "$" + match.group(1) + "$"
                    arg = match.group(2)
                    expression = expression.replace("\\" + func + "\\left" + tag + "(" + arg + "\\right)" + tag, func + "(" + arg + ")")
                
                match = re.search(r'\\' + func + r'([\;\:\.\,α-ωΑ-Ωa-zA-Z0-9°]+)\^\£([0-9]+)\£\{(.+)\}\£\2\£', expression)
                if match:
                    arg = match.group(1)
                    tag = "£" + match.group(2) + "£"
                    exp = match.group(3)
                    expression = expression.replace("\\" + func + arg + "^" + tag + "{" + exp + "}" + tag, func + "(" + arg + "^(" + exp + "))")

                match = re.search(r'\\' + func + r'([\;\:\.\,α-ωΑ-Ωa-zA-Z0-9°]+)\^([α-ωΑ-Ωa-zA-Z0-9°])', expression)
                if match:
                    arg = match.group(1)
                    exp = match.group(2)
                    expression = expression.replace("\\" + func + arg + "^" + exp, func + "(" + arg + "^" + exp + ")")

                match = re.search(r'\\' + func + r'([\;\:\.\,α-ωΑ-Ωa-zA-Z0-9°]+)', expression)
                if match:
                    arg = match.group(1)
                    expression = expression.replace("\\" + func + arg, func + "(" + arg + ")")
        
        return expression

    def translateSum(self, expression):
        for i in range(expression.count("\\sum")):
            match = re.search(r'\\sum_\£(\d+)\£\{(.+)\=(.+)\}\£\1\£\^\£(\d+)\£\{(.+)\}\£\4\£\\left\$(\d+)\$\((.+)\\right\)\$\6\$', expression)
            if match:
                tag1 = match.group(1)
                lower = match.group(2)
                lower2 = match.group(3)
                tag2 = match.group(4)
                upper = match.group(5)
                tag3 = match.group(6)
                to_be_summed = match.group(7)
                tag_1 = "£" + tag1 + "£"
                tag_2 = "£" + tag2 + "£"
                tag_3 = "$" + tag3 + "$"
                expression = expression.replace("\\sum_" + tag_1 + "{" + lower + "=" + lower2 + "}" + tag_1 + "^" + tag_2 + "{" + upper + "}" + tag_2 + "\\left" + tag_3 + "(" + to_be_summed + "\\right)" + tag_3, "∑(" + to_be_summed + "," + lower + "," + lower2 + "," + upper + ")")

            match = re.search(r'\\sum_\£(\d+)\£\{(.+)\=(.+)\}\£\1\£\^([α-ωΑ-Ωa-zA-Z0-9])\\left\$(\d+)\$\((.+)\\right\)\$\5\$', expression)
            if match:
                tag1 = match.group(1)
                lower = match.group(2)
                lower2 = match.group(3)
                upper = match.group(4)
                tag3 = match.group(5)
                to_be_summed = match.group(6)
                tag_1 = "£" + tag1 + "£"
                tag_3 = "$" + tag3 + "$"
                expression = expression.replace("\\sum_" + tag_1 + "{" + lower + "=" + lower2 + "}" + tag_1 + "^" + upper + "\\left" + tag_3 + "(" + to_be_summed + "\\right)" + tag_3, "∑(" + to_be_summed + "," + lower + "," + lower2 + "," + upper + ")")

            match = re.search(r'\\sum_\£(\d+)\£\{(.+)\=(.+)\}\£\1\£\^\£(\d+)\£\{(.+)\}\£\4\£([\;\:\.\,α-ωΑ-Ωa-zA-Z0-9°]+)', expression)
            if match:
                tag1 = match.group(1)
                lower = match.group(2)
                lower2 = match.group(3)
                tag2 = match.group(4)
                upper = match.group(5)
                to_be_summed = match.group(6)
                tag_1 = "£" + tag1 + "£"
                tag_2 = "£" + tag2 + "£" # \sum _{3=x}^w\left(d+1\right)
                expression = expression.replace("\\sum_" + tag_1 + "{" + lower + "=" + lower2 + "}" + tag_1 + "^" + tag_2 + "{" + upper + "}" + tag_2 + to_be_summed, "∑(" + to_be_summed + "," + lower + "," + lower2 + "," + upper + ")")

            match = re.search(r'\\sum_\£(\d+)\£\{(.+)\=(.+)\}\£\1\£\^([α-ωΑ-Ωa-zA-Z0-9])([\;\:\.\,α-ωΑ-Ωa-zA-Z0-9°]+)', expression)
            if match:
                    tag1 = match.group(1)
                    lower = match.group(2)
                    lower2 = match.group(3)
                    upper = match.group(4)
                    to_be_summed = match.group(5)
                    tag_1 = "£" + tag1 + "£"
                    expression = expression.replace("\\sum_" + tag_1 + "{" + lower + "=" + lower2 + "}" + tag_1 + "^" + upper + to_be_summed, "∑(" + to_be_summed + "," + lower + "," + lower2 + "," + upper + ")")
        return expression

    def translateProd(self, expression):
        for i in range(expression.count("\\prod")):
            match = re.search(r'\\prod_\£(\d+)\£\{(.+)\=(.+)\}\£\1\£\^\£(\d+)\£\{(.+)\}\£\4\£\\left\$(\d+)\$\((.+)\\right\)\$\6\$', expression)
            if match:
                tag_1 = "£" + match.group(1) + "£"
                lower = match.group(2)
                lower2 = match.group(3)
                tag_2 = "£" + match.group(4) + "£"
                upper = match.group(5)
                tag_3 = "$" + match.group(6) + "$"
                to_be_summed = match.group(7)
                
                expression = expression.replace("\\prod_" + tag_1 + "{" + lower + "=" + lower2 + "}" + tag_1 + "^" + tag_2 + "{" + upper + "}" + tag_2 + "\\left" + tag_3 + "(" + to_be_summed + "\\right)" + tag_3,
                                                "∏(" + to_be_summed + "," + lower + "," + lower2 + "," + upper + ")"
                                                )
                
            match = re.search(r'\\prod_\£(\d+)\£\{(.+)\=(.+)\}\£\1\£\^([α-ωΑ-Ωa-zA-Z0-9])\\left\$(\d+)\$\((.+)\\right\)\$\5\$', expression)
            if match:
                tag_1 = "£" + match.group(1) + "£"
                lower = match.group(2)
                lower2 = match.group(3)
                upper = match.group(4)
                tag_3 = "$" + match.group(5) + "$"
                to_be_summed = match.group(6)
                expression = expression.replace("\\prod_" + tag_1 + "{" + lower + "=" + lower2 + "}" + tag_1 + "^" + upper + "\\left" + tag_3 + "(" + to_be_summed + "\\right)" + tag_3, "∏(" + to_be_summed + "," + lower + "," + lower2 + "," + upper + ")")

            match = re.search(r'\\prod_\£(\d+)\£\{(.+)\=(.+)\}\£\1\£\^\£(\d+)\£\{(.+)\}\£\4\£([\;\:\.\,α-ωΑ-Ωa-zA-Z0-9°]+)', expression)
            if match:
                tag_1 = "£" + match.group(1) + "£"
                lower = match.group(2)
                lower2 = match.group(3)
                tag_2 = "£" + match.group(4) + "£"
                upper = match.group(5)
                to_be_summed = match.group(6)
                expression = expression.replace("\\prod_" + tag_1 + "{" + lower + "=" + lower2 + "}" + tag_1 + "^" + tag_2 + "{" + upper + "}" + tag_2 + to_be_summed, "∏(" + to_be_summed + "," + lower + "," + lower2 + "," + upper + ")")

            match = re.search(r'\\prod_\£(\d+)\£\{(.+)\=(.+)\}\£\1\£\^([α-ωΑ-Ωa-zA-Z0-9])([\;\:\.\,α-ωΑ-Ωa-zA-Z0-9°]+)', expression)
            if match:
                tag_1 = "£" + match.group(1) + "£"
                lower = match.group(2)
                lower2 = match.group(3)
                upper = match.group(4)
                to_be_summed = match.group(5)
                expression = expression.replace("\\prod_" + tag_1 + "{" + lower + "=" + lower2 + "}" + tag_1 + "^" + upper + to_be_summed, "∏(" + to_be_summed + "," + lower + "," + lower2 + "," + upper + ")")        
        return expression

    def translateCombinations(self, expression):
        sym = "," if self.TI_on else ";"
        for i in range(expression.count("\\binom")):
            match = re.search(r'\\binom\£(\d+)\£\{(.+)\}\£\1\£\£(\d+)\£\{(.+)\}\£\3\£', expression)
            if match:
                tag_1 = "£" + match.group(1) + "£"
                upper = match.group(2)
                tag_2 = "£" + match.group(3) + "£"
                lower = match.group(4)

                string = "\\binom" + tag_1 + "{" + upper + "}" + tag_1 + tag_2 + "{" + lower + "}" + tag_2
                expression = expression.replace(string, "nCr(" + upper + sym + lower + ")")    
        return expression

    def translateLimits(self, expression):
        # \lim _{x\rightarrow \infty ^-}\left(x+1\right)
        for i in range(expression.count("\\lim")):
            match = re.search(r'\\lim_\£(\d+)\£\{(.+?)\\rightarrow(.+)\^([\+\-])\}\£\1\£\\left\$(\d+)\$\((.+)\\right\)\$\5\$', expression) # ^+-
            if match:
                tag_1 = "£" + match.group(1) + "£"
                variable = match.group(2)
                approaching = match.group(3)
                pm = match.group(4)
                tag_2 = "$" + match.group(5) + "$"
                function = match.group(6)

                string = "\\lim_" + tag_1 + "{" + variable + "\\rightarrow" + approaching + "^" + pm + "}" + tag_1 + "\\left" + tag_2 + "(" + function + "\\right)" + tag_2
                replacement = ("lim(" + function + "," + variable + "," + approaching + ",1)"
                            if pm == "+" else
                            "lim(" + function + "," + variable + "," + approaching + "," + pm + "1)"
                            )
                expression = expression.replace(string, replacement)
                
            
            match = re.search(r'\\lim_\£(\d+)\£\{(.+?)\\rightarrow(.+)\}\£\1\£\\left\$(\d+)\$\((.+)\\right\)\$\4\$', expression)
            if match:
                tag_1 = "£" + match.group(1) + "£"
                variable = match.group(2)
                approaching = match.group(3)
                tag_2 = "$" + match.group(4) + "$"
                function = match.group(5)
                expression = expression.replace("\\lim_" + tag_1 + "{" + variable + "\\rightarrow" + approaching + "}" + tag_1 + "\\left" + tag_2 + "(" + function + "\\right)" + tag_2,
                                                "lim(" + function + "," + variable + "," + approaching + ")"
                                                )

        return expression

    def translatePermutations(self, expression):
        sym = "," if self.TI_on else ";"

        for i in range(expression.count("_")):
            match = re.search(r'\\left\$(\d+)\$\((.+)\\right\)\$\1\$_\£(\d+)\£\{(.+)\}\£\3\£', expression)
            if match:
                tag1 = "$" + match.group(1) + "$"
                n = match.group(2)
                tag2 = "£" + match.group(3) + "£"
                r = match.group(4)
                string = "\\left" + tag1 + "(" + n + "\\right)" + tag1 + "_" + tag2 + "{" + r + "}" + tag2
                expression = expression.replace(string, "nPr(" + n + sym + r + ")")

            match = re.search(r'\\left\$(\d+)\$\((.+)\\right\)\$\1\$_([α-ωΑ-Ωa-zA-Z0-9])', expression)
            if match:
                tag1 = "$" + match.group(1) + "$"
                n = match.group(2)
                r = match.group(3)
                string = "\\left" + tag1 + "(" + n + "\\right)" + tag1 + "_" + r
                expression = expression.replace(string, "nPr(" + n + sym + r + ")")
        return expression

    def translateFractions(self, expression):
        for i in range(expression.count("\\frac")):
            match = re.search(r'\\frac\£(\d+)\£\{(.+)\}\£\1\£\£(\d+)\£\{(.+)\}\£\3\£', expression)
            if match:
                tag1 = "£" + match.group(1) + "£"
                numerator = match.group(2)
                tag2 = "£" + match.group(3) + "£"
                denominator = match.group(4)
                expression = expression.replace("\\frac" + tag1 + "{" + numerator + "}" + tag1 + tag2 + "{" + denominator + "}" + tag2, f"(({numerator})/({denominator}))")
        return expression

    # OPTIMIZE
    def translateLn(self, expression):
        if "\\ln" not in expression:
            return expression
        # test \begin{cases}\begin{matrix}\pi ^{\ln \Delta ^{\Omega }}&\ln \sigma ^{\frac{\tau }{2}}\\\ln x^2&\ln \left(i\right)^3\end{matrix}=\ln a\ln d-\ln b\ln c&\\\frac{\ln \left(\ln x^2\right)^3}{\ln y}=\ln \alpha ^{\ln \left(\beta -1\right)^{-u\ln w}}&\end{cases}
        expression = re.sub(r'\\ln\\left\$([0-9]+)\$\((.+)\\right\)\$\1\$', r'ln(\2)', expression)
        expression = re.sub(r'\\ln([\;\:\.\,α-ωΑ-Ωa-zA-Z0-9°]+)\^\£([0-9]+)\£\{(.+)\}\£\2\£', r'ln(\1^(\3))', expression)
        expression = re.sub(r'\\ln([\;\:\.\,α-ωΑ-Ωa-zA-Z0-9°]+)\^([α-ωΑ-Ωa-zA-Z0-9°])', r'ln(\1^\2)', expression)
        expression = re.sub(r'\\ln([\;\:\.\,α-ωΑ-Ωa-zA-Z0-9°]+)', r'ln(\1)', expression)

        return expression

    # OPTIMIZE
    def translateLog(self, expression):
        if "\\log" not in expression:
            return expression
        if self.TI_on:
            for i in range(expression.count("\\log_")):
                match = re.search(r'\\log_\£([0-9]+)\£\{(.+)\}\£\1\£\\left\$([0-9]+)\$\((.+)\\right\)\$\3\$', expression)
                if match:
                    tagp = "£" + match.group(1) + "£"
                    base = match.group(2)
                    tagd = "$" + match.group(3) + "$"
                    arg = match.group(4)
                    expression = expression.replace("\\log_" + tagp + "{" + base + "}" + tagp + "\\left" + tagd + "(" + arg + "\\right)" + tagd, "log(" + arg + "," + base + ")")

                match = re.search(r'\\log_([\;\:\.\,α-ωΑ-Ωa-zA-Z0-9°])\\left\$([0-9]+)\$\((.+)\\right\)\$\2\$', expression)
                if match:
                    base = match.group(1)
                    tag = "$" + match.group(2) + "$"
                    arg = match.group(3)
                    expression = expression.replace("\\log_" + base + "\\left" + tag + "(" + arg + "\\right)" + tag, "log(" + arg + "," + base + ")")

                match = re.search(r'\\log_\£([0-9]+)\£\{(.+)\}\£\1\£([\;\:\.\,α-ωΑ-Ωa-zA-Z0-9°]+)\^\£([0-9]+)\£\{(.+)\}\£\4\£', expression)
                if match:
                    tag_1 = "£" + match.group(1) + "£"
                    base = match.group(2)
                    arg = match.group(3)
                    tag_2 = "£" + match.group(4) + "£"
                    exp = match.group(5)
                    expression = expression.replace("\\log_" + tag_1 + "{" + base + "}" + tag_1 + arg + "^" + tag_2 + "{" + exp + "}" + tag_2, "log(" + arg + "^(" + exp + ")," + base + ")")

                match = re.search(r'\\log_\£([0-9]+)\£\{(.+)\}\£\1\£([\;\:\.\,α-ωΑ-Ωa-zA-Z0-9°]+)\^([\;\:\.\,α-ωΑ-Ωa-zA-Z0-9°])', expression)
                if match:
                    tag = "£" + match.group(1) + "£"
                    base = match.group(2)
                    arg = match.group(3)
                    exp = match.group(4)
                    expression = expression.replace("\\log_" + tag + "{" + base + "}" + tag + arg + "^" + exp, "log(" + arg + "^" + exp + "," + base + ")")

                match = re.search(r'\\log_\£([0-9]+)\£\{(.+)\}\£\1\£([\;\:\.\,α-ωΑ-Ωa-zA-Z0-9°]+)', expression)
                if match:
                    tag = "£" + match.group(1) + "£"
                    base = match.group(2)
                    arg = match.group(3)
                    expression = expression.replace("\\log_" + tag + "{" + base + "}" + tag + arg, "log(" + arg + "," + base + ")")

                match = re.search(r'\\log_([\;\:\.\,α-ωΑ-Ωa-zA-Z0-9°])\\left\$([0-9]+)\$\((.+)\\right\)\$\2\$', expression)
                if match:
                    base = match.group(1)
                    tag = "$" + match.group(2) + "$"
                    arg = match.group(3)
                    expression = expression.replace("\\log_" + base + "\\left" + tag + "("+ arg + "\\right)" + tag, "log(" + arg + "," + base + ")")
                        
                match = re.search(r'\\log_([\;\:\.\,α-ωΑ-Ωa-zA-Z0-9°])([\;\:\.\,α-ωΑ-Ωa-zA-Z0-9°]+)\^\£([0-9]+)\£\{(.+)\}\£\3\£', expression)
                if match:
                    base = match.group(1)
                    arg = match.group(2)
                    tag = "£" + match.group(3) + "£"
                    exp = match.group(4)
                    expression = expression.replace("\\log_" + base + arg + "^" + tag + "{" + exp + "}" + tag, "log(" + arg + "^(" + exp + ")," + base + ")")


                match = re.search(r'\\log_([\;\:\.\,α-ωΑ-Ωa-zA-Z0-9°])([\;\:\.\,α-ωΑ-Ωa-zA-Z0-9°]+)\^([\;\:\.\,α-ωΑ-Ωa-zA-Z0-9°])', expression)
                if match:
                    base = match.group(1)
                    arg = match.group(2)
                    exp = match.group(3)
                    expression = expression.replace("\\log_" + base + arg + "^" + exp, "log(" + arg + "^" + exp + "," + base + ")")

                match = re.search(r'\\log_([\;\:\.\,α-ωΑ-Ωa-zA-Z0-9°])([\;\:\.\,α-ωΑ-Ωa-zA-Z0-9°]+)', expression)
                if match:
                    base = match.group(1)
                    arg = match.group(2)
                    expression = expression.replace("\\log_" + base + arg, "log(" + arg + "," + base + ")")

            # log without base
            for i in range(expression.count("\\log")):
                match = re.search(r'\\log\\left\$([0-9]+)\$\((.+)\\right\)\$\1\$', expression)
                if match:
                    tag = "$" + match.group(1) + "$"
                    arg = match.group(2)
                    expression = expression.replace("\\log\\left" + tag + "(" + arg + "\\right)" + tag, "log(" + arg + ",10)")

                match = re.search(r'\\log([\;\:\.\,α-ωΑ-Ωa-zA-Z0-9°]+)\^\£([0-9]+)\£\{(.+)\}\£\2\£', expression)
                if match:
                    arg = match.group(1)
                    tag = "£" + match.group(2) + "£"
                    exp = match.group(3)
                    expression = expression.replace("\\log" + arg + "^" + tag + "{" + exp + "}" + tag, "log(" + arg + "^(" + exp + "),10)")

                match = re.search(r'\\log([\;\:\.\,α-ωΑ-Ωa-zA-Z0-9°]+)\^([α-ωΑ-Ωa-zA-Z0-9°])', expression)
                if match:
                    arg = match.group(1)
                    exp = match.group(2)
                    expression = expression.replace("\\log" + arg + "^" + exp, "log(" + arg + "^" + exp + ",10)")

                match = re.search(r'\\log([\;\:\.\,α-ωΑ-Ωa-zA-Z0-9°]+)', expression)
                if match:
                    arg = match.group(1)
                    expression = expression.replace("\\log" + arg, "log(" + arg + ",10)")

        else:
        # log with base
            for i in range(expression.count("\\log_")):
                match = re.search(r'\\log_\£([0-9]+)\£\{(.+)\}\£\1\£\\left\$([0-9]+)\$\((.+)\\right\)\$\3\$', expression)
                if match:
                    tagp = "£" + match.group(1) + "£"
                    base = match.group(2)
                    tagd = "$" + match.group(3) + "$"
                    arg = match.group(4)
                    expression = expression.replace("\\log_" + tagp + "{" + base + "}" + tagp + "\\left" + tagd + "(" + arg + "\\right)" + tagd, "log(" + base + ";" + arg + ")")

                match = re.search(r'\\log_([\;\:\.\,α-ωΑ-Ωa-zA-Z0-9°])\\left\$([0-9]+)\$\((.+)\\right\)\$\2\$', expression)
                if match:
                    base = match.group(1)
                    tag = "$" + match.group(2) + "$"
                    arg = match.group(3)
                    expression = expression.replace("\\log_" + base + "\\left" + tag + "(" + arg + "\\right)" + tag, "log(" + base + ";" + arg + ")")

                match = re.search(r'\\log_\£([0-9]+)\£\{(.+)\}\£\1\£([\;\:\.\,α-ωΑ-Ωa-zA-Z0-9°]+)\^\£([0-9]+)\£\{(.+)\}\£\4\£', expression)
                if match:
                    tag_1 = "£" + match.group(1) + "£"
                    base = match.group(2)
                    arg = match.group(3)
                    tag_2 = "£" + match.group(4) + "£"
                    exp = match.group(5)
                    expression = expression.replace("\\log_" + tag_1 + "{" + base + "}" + tag_1 + arg + "^" + tag_2 + "{" + exp + "}" + tag_2, "log(" + base + ";" +  arg + "^(" + exp + "))")

                match = re.search(r'\\log_\£([0-9]+)\£\{(.+)\}\£\1\£([\;\:\.\,α-ωΑ-Ωa-zA-Z0-9°]+)\^([\;\:\.\,α-ωΑ-Ωa-zA-Z0-9°])', expression)
                if match:
                    tag = "£" + match.group(1) + "£"
                    base = match.group(2)
                    arg = match.group(3)
                    exp = match.group(4)
                    expression = expression.replace("\\log_" + tag + "{" + base + "}" + tag + arg + "^" + exp, "log(" + base + ";" + arg + "^" + exp + ")")

                match = re.search(r'\\log_\£([0-9]+)\£\{(.+)\}\£\1\£([\;\:\.\,α-ωΑ-Ωa-zA-Z0-9°]+)', expression)
                if match:
                    tag = "£" + match.group(1) + "£"
                    base = match.group(2)
                    arg = match.group(3)
                    expression = expression.replace("\\log_" + tag + "{" + base + "}" + tag + arg, "log(" + base + ";" + arg + ")")

                match = re.search(r'\\log_([\;\:\.\,α-ωΑ-Ωa-zA-Z0-9°])\\left\$([0-9]+)\$\((.+)\\right\)\$\2\$', expression)
                if match:
                    base = match.group(1)
                    tag = "$" + match.group(2) + "$"
                    arg = match.group(3)
                    expression = expression.replace("\\log_" + base + "\\left" + tag + "("+ arg + "\\right)" + tag, "log(" + base + ";" + arg + ")")
                        
                match = re.search(r'\\log_([\;\:\.\,α-ωΑ-Ωa-zA-Z0-9°])([\;\:\.\,α-ωΑ-Ωa-zA-Z0-9°]+)\^\£([0-9]+)\£\{(.+)\}\£\3\£', expression)
                if match: 
                    base = match.group(1)
                    arg = match.group(2)
                    tag = "£" + match.group(3) + "£"
                    exp = match.group(4)
                    expression = expression.replace("\\log_" + base + arg + "^" + tag + "{" + exp + "}" + tag, "log(" + base + ";" + arg + "^(" + exp + "))")


                match = re.search(r'\\log_([\;\:\.\,α-ωΑ-Ωa-zA-Z0-9°])([\;\:\.\,α-ωΑ-Ωa-zA-Z0-9°]+)\^([\;\:\.\,α-ωΑ-Ωa-zA-Z0-9°])', expression)
                if match:
                    base = match.group(1)
                    arg = match.group(2)
                    exp = match.group(3)
                    expression = expression.replace("\\log_" + base + arg + "^" + exp, "log(" + base + ";" + arg + "^" + exp + ")")

                match = re.search(r'\\log_([\;\:\.\,α-ωΑ-Ωa-zA-Z0-9°])([\;\:\.\,α-ωΑ-Ωa-zA-Z0-9°]+)', expression)
                if match:
                    base = match.group(1)
                    arg = match.group(2)
                    expression = expression.replace("\\log_" + base + arg, "log(" + base + ";" + arg + ")")

            # log without base
            for i in range(expression.count("\\log")):
                match = re.search(r'\\log\\left\$([0-9]+)\$\((.+)\\right\)\$\1\$', expression)
                if match:
                    tag = "$" + match.group(1) + "$"
                    arg = match.group(2)
                    expression = expression.replace("\\log\\left" + tag + "(" + arg + "\\right)" + tag, "log(10;" + arg + ")")
                
                match = re.search(r'\\log([\;\:\.\,α-ωΑ-Ωa-zA-Z0-9°]+)\^\£([0-9]+)\£\{(.+)\}\£\2\£', expression)
                if match:
                    arg = match.group(1)
                    tag = "£" + match.group(2) + "£"
                    exp = match.group(3)
                    expression = expression.replace("\\log" + arg + "^" + tag + "{" + exp + "}" + tag, "log(10;" + arg + "^(" + exp + "))")

                match = re.search(r'\\log([\;\:\.\,α-ωΑ-Ωa-zA-Z0-9°]+)\^([α-ωΑ-Ωa-zA-Z0-9°])', expression)
                if match:
                    arg = match.group(1)
                    exp = match.group(2)
                    expression = expression.replace("\\log" + arg + "^" + exp, "log(10;" + arg + "^" + exp + ")")

                match = re.search(r'\\log([\;\:\.\,α-ωΑ-Ωa-zA-Z0-9°]+)', expression)
                if match:
                    arg = match.group(1)
                    expression = expression.replace("\\log" + arg, "log(10;" + arg + ")")

        return expression

    def translateLg(self, expression):
        if "\\lg" not in expression:
            return expression
        
        replacementPattern = r'log(\2,10)' if self.TI_on else r'log(10;\2)'
        expression = re.sub(r'\\lg\\left\$([0-9]+)\$\((.+)\\right\)\$\1\$', replacementPattern, expression)

        replacementPattern = r'log(\1^(\3),10)' if self.TI_on else r'log(10;\1^(\3))'
        expression = re.sub(r'\\lg([\;\:\.\,α-ωΑ-Ωa-zA-Z0-9°]+)\^\£([0-9]+)\£\{(.+)\}\£\2\£', replacementPattern, expression)

        replacementPattern = r'log(\1^\2,10)' if self.TI_on else r'log(10;\1^\2)'
        expression = re.sub(r'\\lg([\;\:\.\,α-ωΑ-Ωa-zA-Z0-9°]+)\^([α-ωΑ-Ωa-zA-Z0-9°])', replacementPattern, expression)
                            
        replacementPattern = r'log(\1,10)' if self.TI_on else r'log(10;\1)'
        expression = re.sub(r'\\lg([\;\:\.\,α-ωΑ-Ωa-zA-Z0-9°]+)', replacementPattern, expression)
      
        return expression

    def translateSqrt(self, expression):
        for i in range(expression.count("\\sqrt")):
            match = re.search(r'\\sqrt\`([0-9]+)\`\[(.+)\]\`\1\`\£([0-9]+)\£\{(.+)\}\£\3\£', expression)
            if match:
                tagq = "`" + match.group(1) + "`"
                n = match.group(2)
                tagp = "£" + match.group(3) + "£"
                x = match.group(4)
                string = "\\sqrt" + tagq + "[" + n + "]" + tagq + tagp + "{" + x + "}" + tagp
                replacement = "root(" + x + "," + n + ")" if self.TI_on else "(" + x + ")^(1/(" + n + "))"

                expression = expression.replace(string, replacement)
        
            match = re.search(r'\\sqrt\£([0-9]+)\£\{(.+)\}\£\1\£', expression)
            if match:
                tag = "£" + match.group(1) + "£"    
                x = match.group(2)

                expression = expression.replace("\\sqrt" + tag + "{" + x + "}" + tag, "sqrt(" + x + ")")
        return expression

    def translateSystem(self, expression):

        if "\\begin" in expression:
            expression = expression.replace("end", "enj")
            
            # Replace \\begin£<number>£{cases}£<number>£ with system(
            expression = re.sub(r'\\begin£([0-9]+)£\{cases\}£\1£', r'system(', expression)

            # Replace &<content>\\enj£<number>£{cases}£<number>£ with <content>)
            expression = re.sub(r'&([^\\]*)\\enj£([0-9]+)£\{cases\}£\2£', r' \1)', expression)

            # Handle cases without &
            expression = re.sub(r'\\enj£([0-9]+)£\{cases\}£\1£', r')', expression)

            # Replace &<content>\\ with <content>, 
            expression = re.sub(r'&([^\\]*)\\\\', r' \1,', expression)
            
            # Replace <content>\\ with <content>, for cases without &
            if '&' not in expression:
                expression = re.sub(r'([^&\\]+)\\\\', r'\1,', expression)




        return expression

    # OPTIMIZE
    def translateIntegrals(self, expression):
        if "\\int_" in expression:
            expression = expression.replace("\\int_", "¤") 
            
            old_expression = expression
            expression = "¤" + expression + "d"
            result = regex.search(r'(?<rec>¤(?:[^¤d]++|(?&rec))*d)', expression, flags=regex.VERBOSE)
            expression = old_expression
            if result:
                matches = result.captures('rec')        
                matches.sort(key=len, reverse=True)    
                                                      
                copy_list = []
                for index, match in enumerate(matches):
                    copy_list.append(match)
                    tag = "§" + str(index) + "§"
                    amount = copy_list.count(match)
                    expression = expression.replace(match, "###", amount-1)
                    expression = expression.replace(match, tag + match + tag, 1)
                    expression = expression.replace("###", match, amount-1)
            
            for i in range(expression.count("¤")):
                # \int _{12}^{34}xdx
                match = re.search(r'\§(\d+)\§¤\£(\d+)\£\{(.+)\}\£\2\£\^\£(\d+)\£\{(.+)\}\£\4\£(.+)d\§\1\§([a-ce-zA-Z0-9α-ωΑ-Ω])', expression)
                
                if match:
                    tagInt = "§" + match.group(1) + "§"
                    tag1 = "£" + match.group(2) + "£"
                    lower = match.group(3)
                    tag2 = "£" + match.group(4) + "£"
                    upper = match.group(5)
                    integrand = match.group(6)
                    variable = match.group(7)
                    expression = expression.replace(
                        tagInt + "¤" + tag1 + "{" + lower + "}" + tag1 + "^" + tag2 + "{" + upper + "}" + tag2 + integrand + "d" + tagInt + variable,
                        "∫((" + integrand + "),(" + variable + "),(" + lower + "),(" + upper + "))"
                        )
                    
                # \int _{12}^3xdx
                match = re.search(r'\§(\d+)\§¤\£(\d+)\£\{(.+)\}\£\2\£\^([a-ce-zA-Z0-9α-ωΑ-Ω])(.+)d\§\1\§([a-ce-zA-Z0-9α-ωΑ-Ω])', expression)
                if match:
                    tagInt = "§" + match.group(1) + "§"
                    tag1 = "£" + match.group(2) + "£"
                    lower = match.group(3)
                    upper = match.group(4)
                    integrand = match.group(5)
                    variable = match.group(6)
                    expression = expression.replace(
                        tagInt + "¤" + tag1 + "{" + lower + "}" + tag1 + "^" + upper + integrand + "d" + tagInt + variable,
                        "∫((" + integrand + "),(" + variable + "),(" + lower + "),(" + upper + "))"
                        )
                # \int _1^{23}xdx
                match = re.search(r'\§(\d+)\§¤([^d])\^\£(\d+)\£\{(.+)\}\£\3\£(.+)d\§\1\§([a-ce-zA-Z0-9α-ωΑ-Ω])', expression)
                if match:
                    tagInt = "§" + match.group(1) + "§"
                    lower = match.group(2)
                    tag2 = "£" + match.group(3) + "£"
                    upper = match.group(4)
                    integrand = match.group(5)
                    variable = match.group(6)
                    expression = expression.replace(
                        tagInt + "¤" + lower + "^" + tag2 + "{" + upper + "}" + tag2 + integrand + "d" + tagInt + variable,
                        "∫((" + integrand + "),(" + variable + "),(" + lower + "),(" + upper + "))"
                        )
                # \int _1^2xdx
                match = re.search(r'\§(\d+)\§¤([a-ce-zA-Z0-9α-ωΑ-Ω])\^([a-ce-zA-Z0-9α-ωΑ-Ω])(.+)d\§\1\§([a-ce-zA-Z0-9α-ωΑ-Ω])', expression)
                if match:
                    tagInt = "§" + match.group(1) + "§"
                    lower = match.group(2)
                    upper = match.group(3)
                    integrand = match.group(4)
                    variable = match.group(5)
                    expression = expression.replace(
                        tagInt + "¤" + lower + "^" + upper + integrand + "d" + tagInt + variable,
                        "∫((" + integrand + "),(" + variable + "),(" + lower + "),(" + upper + "))"
                    )
                    
                # \int _{ }^{ }x\ dx
                match = re.search(r'\§(\d+)\§¤\£(\d+)\£{}\£\2\£\^\£(\d+)\£{}\£\3\£(.+)d\§\1\§([a-ce-zA-Z0-9α-ωΑ-Ω])', expression)
                if match:
                    tagInt = "§" + match.group(1) + "§"
                    tag1 = match.group(2)
                    tag2 = match.group(3)
                    integrand = match.group(4)
                    variable = match.group(5)
                    tag_1 = "£" + tag1 + "£"
                    tag_2 = "£" + tag2 + "£"
                    expression = expression.replace(
                        tagInt + "¤" + tag_1 + "{}" + tag_1 + "^" + tag_2 + "{}" + tag_2 + integrand + "d" + tagInt + variable,
                        "∫((" + integrand + "),(" + variable + "))"
                        )
        
        return expression

    def translateDerivatives(self, expression):
        derivative = False
        
        if re.search(r"\{d\S\}", expression):
            derivative = True
            
        if re.search(r"D", expression):
            expression = expression.replace("D", r"{{d}/{dx}}")
            derivative = True
            
        if derivative:
            # Match pattern for {d followed by any non-space character
            pattern = r"\{d\S\}"
            matches = list(re.finditer(pattern, expression))

            for match in matches:
                left_count = 0
                right_count = 0
                start_position = match.end()
                final_right_pos = -1

                # Find matching bracket
                for match2 in re.finditer(r"\\left|\\right", expression[start_position:]):
                    if match2.group() == r"\left":
                        left_count += 1
                    elif match2.group() == r"\right":
                        right_count += 1

                        if left_count == right_count:
                            final_right_pos = start_position + match2.start()
                            break

                if final_right_pos != -1:
                    # Add the derivative variable to the expression
                    expression = expression[:final_right_pos] + "," + match.group(0).replace("{d", "").replace("}", "") + expression[final_right_pos:]

            return expression
            
        
        return expression
    # OPTIMIZE
    def translateVectors(self, expression):
        if not ("𝕚" in expression or "ӄ" in expression or "𝕛" in expression or "matrix" in expression or "bar" in expression or "`" in expression or "overline" in expression):
            return expression
        expression = expression.replace("end", "enj")
        if 'ӄ' in expression:
            kVector = True
        else:
            kVector = False

        vector = False
        for i in range(expression.count("matrix") // 2):

            match = re.search(r'\\left\`(\d+)\`\[\\begin\£(\d+)\£\{matrix\}\£\2\£(.+)\\\\(.+)\\enj\£(\d+)\£\{matrix\}\£\5\£\\right\]\`\1\`', expression)

            if match:
                tag1 = '`' + match.group(1) + '`'
                tag2 = '£' + match.group(2) + '£'
                xComponent = match.group(3)
                yComponent = match.group(4)
                tag3 = '£' + match.group(5) + '£'
                matrix = '{matrix}'
                if '\\\\' in xComponent:
                    xyComponents = xComponent.split('\\\\')
                    zComponent = yComponent
                    xComponent = xyComponents[0]
                    yComponent = xyComponents[1]
                    expression = expression.replace(f'\\left{tag1}[\\begin{tag2}{matrix}{tag2}{xComponent}\\\\{yComponent}\\\\{zComponent}\\enj{tag3}{matrix}{tag3}\\right]{tag1}', f'{tag1}[{xComponent},{yComponent},{zComponent}]{tag1}')
                elif kVector:
                    expression = expression.replace(f'\\left{tag1}[\\begin{tag2}{matrix}{tag2}{xComponent}\\\\{yComponent}\\enj{tag3}{matrix}{tag3}\\right]{tag1}', f'{tag1}[{xComponent},{yComponent},0]{tag1}')
                else:
                    expression = expression.replace(f'\\left{tag1}[\\begin{tag2}{matrix}{tag2}{xComponent}\\\\{yComponent}\\enj{tag3}{matrix}{tag3}\\right]{tag1}', f'{tag1}[{xComponent},{yComponent}]{tag1}')
                vector = True

        # dot product
        if vector:
            print(expression)
            for i in range(expression.count('`') // 2):
                match = re.search(r'\`(\d+)\`\[(.+)\]\`\1\`\*\`(\d+)\`\[(.+)\]\`\3\`', expression)
                if match:
                    tag1 = '`' + match.group(1) + '`'
                    vectorA = match.group(2)
                    tag2 = '`' + match.group(3) + '`'
                    vectorB = match.group(4)
                    expression = expression.replace(f'{tag1}[{vectorA}]{tag1}*{tag2}[{vectorB}]{tag2}', f'dotP([{vectorA}],[{vectorB}])')

        # \bar£1£{u}£1£*\bar£2£{v}£2£
        for i in range(expression.count('\\bar') // 2):
            print(expression)
            match = re.search(r'\\bar\£(\d+)\£\{(.+)\}\£\1\£\*\\bar\£(\d+)\£\{(.+)\}\£\3\£', expression)
            if match:
                tag1 = '£' + match.group(1) + '£'
                vectorA = '{' + match.group(2) + '}'
                tag2 = '£' + match.group(3) + '£'
                vectorB = '{' + match.group(4) + '}'
                expression = expression.replace(f'\\bar{tag1}{vectorA}{tag1}*\\bar{tag2}{vectorB}{tag2}', f'dotP({vectorA},{vectorB})')

        for i in range(expression.count('\\overline') // 2):
            print(expression)
            match = re.search(r'\\overline\£(\d+)\£\{(.+)\}\£\1\£\*\\overline\£(\d+)\£\{(.+)\}\£\3\£', expression)
            if match:
                tag1 = '£' + match.group(1) + '£'
                vectorA = '{' + match.group(2) + '}'
                tag2 = '£' + match.group(3) + '£'
                vectorB = '{' + match.group(4) + '}'
                expression = expression.replace(f'\\overline{tag1}{vectorA}{tag1}*\\overline{tag2}{vectorB}{tag2}', f'dotP({vectorA},{vectorB})')
        
        for i in range(expression.count('\\bar')):
            print(expression)
            match = re.search(r'\\bar\£(\d+)\£\{(.+)\}\£\1\£\*\\overline\£(\d+)\£\{(.+)\}\£\3\£', expression)
            if match:
                tag1 = '£' + match.group(1) + '£'
                vectorA = '{' + match.group(2) + '}'
                tag2 = '£' + match.group(3) + '£'
                vectorB = '{' + match.group(4) + '}'
                expression = expression.replace(f'\\bar{tag1}{vectorA}{tag1}*\\overline{tag2}{vectorB}{tag2}', f'dotP({vectorA},{vectorB})')

        for i in range(expression.count('\\overline')):
            print(expression)
            match = re.search(r'\\overline\£(\d+)\£\{(.+)\}\£\1\£\*\\bar\£(\d+)\£\{(.+)\}\£\3\£', expression)
            if match:
                tag1 = '£' + match.group(1) + '£'
                vectorA = '{' + match.group(2) + '}'
                tag2 = '£' + match.group(3) + '£'
                vectorB = '{' + match.group(4) + '}'
                expression = expression.replace(f'\\overline{tag1}{vectorA}{tag1}*\\bar{tag2}{vectorB}{tag2}', f'dotP({vectorA},{vectorB})')
                
        # cross product        
        if vector:
            for i in range(expression.count('`') // 2):
                match = re.search(r'\`(\d+)\`\[(.+)\]\`\1\`\*ΦcrossΦ\`(\d+)\`\[(.+)\]\`\3\`', expression)
                if match:
                    tag1 = '`' + match.group(1) + '`'
                    vectorA = match.group(2)
                    tag2 = '`' + match.group(3) + '`'
                    vectorB = match.group(4)
                    expression = expression.replace(f'{tag1}[{vectorA}]{tag1}*ΦcrossΦ{tag2}[{vectorB}]{tag2}', f'crossP([{vectorA}],[{vectorB}])')

        # \bar£1£{u}£1£*ΦcrossΦ\bar£2£{v}£2£
        for i in range(expression.count('\\bar') // 2):
            match = re.search(r'\\bar\£(\d+)\£\{(.+)\}\£\1\£\*ΦcrossΦ\\bar\£(\d+)\£\{(.+)\}\£\3\£', expression)
            if match:
                tag1 = '£' + match.group(1) + '£'
                vectorA = '{' + match.group(2) + '}'
                tag2 = '£' + match.group(3) + '£'
                vectorB = '{' + match.group(4) + '}'
                expression = expression.replace(f'\\bar{tag1}{vectorA}{tag1}*ΦcrossΦ\\bar{tag2}{vectorB}{tag2}', f'crossP({vectorA},{vectorB})')

        for i in range(expression.count('\\overline') // 2):
            match = re.search(r'\\overline\£(\d+)\£\{(.+)\}\£\1\£\*ΦcrossΦ\\overline\£(\d+)\£\{(.+)\}\£\3\£', expression)
            if match:
                tag1 = '£' + match.group(1) + '£'
                vectorA = '{' + match.group(2) + '}'
                tag2 = '£' + match.group(3) + '£'
                vectorB = '{' + match.group(4) + '}'
                expression = expression.replace(f'\\overline{tag1}{vectorA}{tag1}*ΦcrossΦ\\overline{tag2}{vectorB}{tag2}', f'crossP({vectorA},{vectorB})')
        
        for i in range(expression.count('\\bar')):
            match = re.search(r'\\bar\£(\d+)\£\{(.+)\}\£\1\£\*ΦcrossΦ\\overline\£(\d+)\£\{(.+)\}\£\3\£', expression)
            if match:
                tag1 = '£' + match.group(1) + '£'
                vectorA = '{' + match.group(2) + '}'
                tag2 = '£' + match.group(3) + '£'
                vectorB = '{' + match.group(4) + '}'
                expression = expression.replace(f'\\bar{tag1}{vectorA}{tag1}*ΦcrossΦ\\overline{tag2}{vectorB}{tag2}', f'crossP({vectorA},{vectorB})')

        for i in range(expression.count('\\overline')):
            match = re.search(r'\\overline\£(\d+)\£\{(.+)\}\£\1\£\*ΦcrossΦ\\bar\£(\d+)\£\{(.+)\}\£\3\£', expression)
            if match:
                tag1 = '£' + match.group(1) + '£'
                vectorA = '{' + match.group(2) + '}'
                tag2 = '£' + match.group(3) + '£'
                vectorB = '{' + match.group(4) + '}'
                expression = expression.replace(f'\\overline{tag1}{vectorA}{tag1}*ΦcrossΦ\\bar{tag2}{vectorB}{tag2}', f'crossP({vectorA},{vectorB})')   
        vector = False
        expression = expression.replace("bar", "").replace("overline", "")

        # vector i, j, k | 𝕚 𝕛 ӄ
        # identifier 𝔦, 𝔧, 𝔨
        
        for i in range(expression.count('𝕚') + expression.count('𝕛') + expression.count('ӄ')):
            if kVector:
                expression = expression.replace('𝕚', f'[1,0,0]', 1).replace('𝕛', f'[0,1,0]', 1).replace('ӄ', f'[0,0,1]', 1)
            else:
                expression = expression.replace('𝕚', f'[1,0]', 1).replace('𝕛', f'[0,1]', 1)
            vector = True
        return expression


    # POISTAA TI alaindeksi kirjaimet?+
    def translateMatrices(self, expression: str):
        if expression.count("matrix") == 0:
            return expression
        expression = expression.replace("end", "enj")
        # tags | 「 」, Ɛ
        expression = re.sub(r'\\begin\£(\d+)\£\{matrix}\£\1\£', r'「', expression)
        expression = re.sub(r'\\enj\£(\d+)\£\{matrix\}\£\1\£', r'」', expression)

        old_expression = expression
        expression = "「" + expression + "」"

        result = regex.search(r'(?<rec>\「(?:[^「」]++|(?&rec))*\」)', expression, flags=regex.VERBOSE)
        expression = old_expression
        if result:
            matches = result.captures('rec')
            matches.sort(key=len, reverse=True)
            copy_list = []
            for index, match in enumerate(matches):
                copy_list.append(match)
                tag = "Ɛ" + str(index) + "Ɛ"
                amount = copy_list.count(match)
                expression = expression.replace(match, "###", amount-1)
                expression = expression.replace(match, tag + match + tag, 1)
                expression = expression.replace("###", match, amount-1)

        
        for i in range(expression.count("「")):
            match = re.search(r'\Ɛ(\d+)\Ɛ\「(.+)\」\Ɛ\1\Ɛ', expression)
            if match:
                tag = f'Ɛ{match.group(1)}Ɛ'
                matrixContents = match.group(2)
                rows = matrixContents.split("\\\\")
                columns = []
                for row in rows:
                    columns.append(row.split("&")) # [[,][,]]

                columnsString = '[' + ', '.join('[{}]'.format(', '.join(map(str, sublist))) for sublist in columns) + ']' # str(columns)
                expression = expression.replace(f'{tag}「{matrixContents}」{tag}', columnsString).replace("'", "").replace(" ", "")
        
        return expression

    def translateSubscripts(self, expression):
        # Define the regex pattern to capture content inside curly braces following an underscore
        pattern = r'_(?:[^{]*?)\{(.*?)\}'

        # Define the subscript digits and the letter mappings
        subscript_digits = "₀₁₂₃₄₅₆₇₈₉"
        indexDict = {
            # az
            "a": "", "b": "", "c": "", "d": "", "e": "", "f": "",
            "g": "", "h": "", "i": "", "j": "", "k": "", "l": "",
            "m": "", "n": "", "o": "", "p": "", "q": "", "r": "",
            "s": "", "t": "", "u": "", "v": "", "w": "", "x": "",
            "y": "", "z": "",

            # AZ
            "A": "", "B": "", "C": "", "D": "", "E": "", "F": "",
            "G": "", "H": "", "I": "", "J": "", "K": "", "L": "",
            "M": "", "N": "", "O": "", "P": "", "Q": "", "R": "",
            "S": "", "T": "", "U": "", "V": "", "W": "", "X": "",
            "Y": "", "Z": ""
        }
        
        # Function to translate characters within the subscript
        def subscript_translator(content):
            translated = ''.join(
                subscript_digits[int(char)] if char.isdigit() else indexDict.get(char, char)
                for char in content
            )
            return translated

        # Find all matches for the pattern
        matches = list(re.finditer(pattern, expression))
        
        for match in matches:
            # Extract the content inside the curly braces
            content = match.group(1)
            # Translate the content
            translated_content = subscript_translator(content)
            # Build the old substring including the curly braces
            old_substring = f'{{{content}}}'
            
            # Replace the old substring with the translated content
            start_index = match.start()
  
            expression = expression[:start_index] + expression[start_index:].replace(old_substring, translated_content, 1)
            # Remove the leading underscore before the replaced content
            # Loop left to find the first underscore
            underscore_pos = start_index 
            while expression[underscore_pos] != '_':
                underscore_pos -= 1

            expression = expression[:underscore_pos] + expression[underscore_pos + 1:]   
            

        return expression
    def removeIdentifiers(self, expression):
        patterns = [r'\£([0-9]+)\£', r'\$([0-9]+)\$', r'\`([0-9]+)\`', r'\§([0-9]+)\§']
        for pattern in patterns:
            expression = re.sub(pattern, r'', expression)
        expression = expression.replace("¤", "int_").replace("⁃", "").replace("』", "")
        return expression



def translate(expression, TI_on=True, SC_on=False, constants_on=False, coulomb_on=False, e_on=False, i_on=False, g_on=False):
    engine = LaTeX2CalcEngine(TI_on, SC_on)
    
    expression = re.sub(r'\\operatorname\{([a-z]+)\}', r'\\\1', expression)
    expression = engine.translateSymbols(expression)
    if TI_on: expression = expression.replace("\\Omega", "Ω").replace(",", ".")

    expression = engine.translateGreekLetters(expression)
    if constants_on:
        expression = engine.translateConstants(expression)
    expression = engine.applyTags(expression)

    expression = engine.translateUnits1(expression)
    expression = engine.translateSum(expression)
    expression = engine.translateProd(expression)
    expression = engine.translateIntegrals(expression) 
    expression = engine.translateCommonFunctions(expression)
    expression = engine.translateLimits(expression)

    expression = engine.translateCombinations(expression) 
    expression = engine.translatePermutations(expression)
    
    expression = engine.translateDerivatives(expression)
    expression = engine.translateFractions(expression)
    # expression = engine.translateLn(expression)
    
    expression = engine.translateLog(expression)
    expression = engine.translateSubscripts(expression)
    expression = engine.translateLg(expression)
    expression = engine.translateSqrt(expression)
    expression = engine.translateSystem(expression)
    expression = engine.translateArrows(expression)
    expression = engine.translateVectors(expression)
    expression = engine.translateMatrices(expression) 
    # TI _unit viimeistely
    expression = engine.translateUnits2(expression) # \mathrm{32\ \frac{kJ}{kg\cdot K}+kJ\cdot \text{kg}-\frac{\text{kJ}}{\text{kg}\cdot \text{K}}} 
    expression = expression.replace("`´`´", "_g").replace("´´´´", "h").replace("````", "g")
    
    if g_on:
        expression = expression.replace("g", "_g")
        # indentattu nyt
        fixG = {
            '\\_': '\\',
            '__gm': '_gm',
            'lo_g': 'log',
            'be_gin': 'begin',
            'i_ght': 'ight'
            }
        for old, new in fixG.items():
            expression = expression.replace(old, new)

    expression = expression.replace("left", "").replace("right", "")
    
    if constants_on: expression = expression.replace("h", "_h").replace("%`´%", "_h")
    # väliaikane korjaus
    expression = expression.replace("__hr", "_hr")
    if coulomb_on: expression = expression.replace("k", "_Cc")
    elif constants_on: expression = expression.replace("k", "_k").replace("Ｇ", "_g")
    
    # lower index
    #expression = engine.translateLowerIndex(expression)

    # remove identifiers
    expression = engine.removeIdentifiers(expression)
    # ≤ & ≥
    expression = expression.replace("\\le", " <=").replace("\\ge", " >=").replace("\\int", "int").replace("\\in", "∈")

    # handle e & i button
    if e_on:
        e_dict = {
            'e': '@e',
            'syst@em': 'system',
            'c@eil': 'ceil',
            'arcs@ec': 'arcsec'
        }
        for key, value in e_dict.items():
            expression = expression.replace(key, value)

    if i_on:
        i_dict = {
            'i': '@i',
            's@in': 'sin',
            'l@im': 'lim',
            'ce@il': 'ceil',
            '@int': 'int'
        }
        for key, value in i_dict.items():
            expression = expression.replace(key, value)
        if e_on:
            expression = expression.replace("c@e@il", "ceil")
    
    expression = expression.replace("\\", "").replace("{", "(").replace("}", ")")
    
    #unicode character U+F008 : <private-use> () used for derivative in Nspire
    expression = re.sub(r"\(\(d\)\/\(d.\)\)", "", expression)  #

    
    # Turn expressions like xy=kc into x*y=k*c
    # Define characters to permute
    characters = ['x', 'y', 'z', 'a', 'b', 'c', 'k']

    # Create regex pattern for permutations of characters
    pattern_xyzabc = re.compile(fr'({"|".join(characters)})+')

    #Remove empty strings before joining with '*'
    def multiplyVariables(match):
        return '*'.join(filter(None, match.group(0)))

    # Apply the replacement function to the expression
    expression = pattern_xyzabc.sub(multiplyVariables, expression)




    def replaceMultiplier(match):
        return match.group(1) + "*("

    def replaceMultiplicand(match):
        return ")*" + match.group(1)
    


    ## Add multiplication sign between non-number and number characters
    def addMultiplicationSign(match):
      return match.group(1) + "*" + match.group(2)
  
    # non-number characters followed by a number 
    expression = re.sub(r'([@\;\:\.\,α-ωΑ-Ωa-zA-Z°₀₁₂₃₄₅₆₇₈₉]+)([0-9]+)', addMultiplicationSign, expression)
    # number followed by a sequence of non-number characters 
    
    
    expression = re.sub(r'([0-9]+)([@\;\:\.\,α-ωΑ-Ωa-zA-Z°₀₁₂₃₄₅₆₇₈₉]+)', addMultiplicationSign, expression)
    # sulkujen kertominen
    expression = re.sub(r'([\@\;\:\.\,α-ωΑ-Ωa-zA-Z0-9°₀₁₂₃₄₅₆₇₈₉]+)\(', replaceMultiplier, expression)
    expression = re.sub(r'\)([\@\;\:\.\,α-ωΑ-Ωa-zA-Z0-9°₀₁₂₃₄₅₆₇₈₉]+)', replaceMultiplicand, expression)
    # fixlist 
    for fix in engine.fixlist:
        expression = expression.replace(fix + "*", fix)

        pattern = r'([\;\:\.\,α-ωΑ-Ωa-zA-Z0-9°₀₁₂₃₄₅₆₇₈₉]+)' + fix
        matches = re.findall(pattern, expression)
        for match in matches:
            expression = expression.replace(match + fix, match + "*" + fix)

    fixAsterisk = {
    "*,": ",",
    "*.": ".",
    "*;": ";",
    "*:": ":",
    "__": "_",
    ",*": ",",
    ".*": ".",
    "*@r": "@r",
    "(*": "(",
    "*)": ")",
    "*°": "°"
    }

    for old_str, new_str in fixAsterisk.items():
        expression = expression.replace(old_str, new_str)

    if g_on:
        for i in range(expression.count("_g")):
            match = re.search(r'_g([a-ln-zA-Zα-ωΑ-Ω@])', expression)
            if match:
                char = match.group(1)
                expression = expression.replace("_g"+char, "_g*" + char, 1)

    if SC_on: expression = expression.replace("π", "(pi)")

    # yleisiä suureyhtälökohtia
    addAsterisk = {
        "mv": "m*v",
     #   "at": "a*t",
      #  "vt": "v*t",
        "mgh": "m*g*h",
      #  "mg": "m*g",
        "ρgh": "ρ*g*h",
      #  "mc": "m*c",
        "cmΔT": "c*m*ΔT",
        "CΔT": "C*ΔT",
        "αl₀ΔT": "α*l₀*ΔT",
        "βl₀ΔT": "β*l₀*ΔT",
        "γl₀ΔT": "γ*l₀*ΔT"
    }
    for org, new in addAsterisk.items():
        expression = expression.replace(org, new)
    
    return expression



# Boolean flags for settings
SC_on = False
TI_on = True
e_on = False
i_on = False
g_on = False
solve_button_on = False
ddx_on = False
constants_on = False
coulomb_on = False


if __name__ == "__main__":
    print(translate(r"\\frac{translatelatex}{ran}"))
else:
    print("Translatelatex.py loaded")
