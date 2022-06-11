MARGINS_NAMES = (
    'ParaLeftMargin',
    'ParaRightMargin',
    'ParaTopMargin',
    'ParaBottomMargin',
)
CONVERT_PARAMETER = 'calc_pdf_Export'

RUN_ARGUMENTS = {
    'host':
        {
            'help': (
                'domain where you want to host API, example: localhost:8070'
            ),
        },
    '--add_margins':
        {
            'help': (
                'By default LibreOffice had very small inner margins in cells.'
                ' If you want increase these margins, set "--add_margins 99". '
                'This way inner margins will seems like in MS Excel '
                '(inaccurate value),'
            ),
            'type': int,
        },
}
