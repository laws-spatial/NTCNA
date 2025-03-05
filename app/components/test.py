def DEBUG(message):
    if True:
        print(message)


class HardcodedDataframeFilter(param.Parameterized):
    df = param.DataFrame(default=None, doc="Source Dataframe")
    df_filtered = param.DataFrame(default=None, doc="Filtered Dataframe")

    reset_filters = param.Action(lambda self: self.reset_filtering())

    channel = param.Range(allow_None=True)
    station_id = param.ListSelector()
    orbit_number = param.Range()
    scan_line_number = param.Range(allow_None=True)
    value_1 = param.Range(allow_None=True)
    value_2 = param.Range(allow_None=True)

    _watcher_filters = param.Parameter(default=None, doc="Internal, Watcher reference")
    ui = param.Parameter(
        default=None, precedence=-1, doc="Panel that holds the filters and table"
    )

    @param.depends("df", on_init=True, watch=True)
    def reset_filtering(self):
        """Resets the DF filtering and the filters. Runs whenever DF changes and during __init__"""
        DEBUG("reset_filtering()")
        if not isinstance(self.df, pd.DataFrame):
            return

        self.df_filtered = self.df
        self.adjust_filters(init_value_range=True)

    def adjust_filters(self, init_value_range=False, *args, **kwargs):
        """Sets the values/value-ranges on the filters based on the *current*
        filtered DF values. This allows the Widget-values to autoadjust to show
        the current values of eg. column 'x' after filtering based on column 'y'.
        Alternatively you may prefer to just keep the widgets as is, then a stripped down
        version of this method can be just merged into the 'reset_filtering()' method
        (and you can base it of self.df, not self.df_filtered)
        """
        DEBUG(
            f"adjust_filters(init_value_range={init_value_range}, args={args}, kwargs={kwargs}"
        )

        # We need to update the filter values but avoid that that is triggering the 'apply_filters'.
        # But at the same time we need to ensure that the filter-widgets UI stuff gets updated by panel.
        # - we can't use "with param.parameterized.discard_events(self), because that would
        #   also block the widgets from being updated
        # - easiest is to just remove our method specific watcher and re-enable it afterwards again
        if self._watcher_filters is not None:
            self.param.unwatch(self._watcher_filters)

        # adjust filter values and, if requested the value-ranges as well.
        # setting value_ranges is only expected to be done when setting/changing the DF.
        # in case the DF gets changed we need to cover for the scenario where the currently
        # set range-of-values (and hence the value) has a wider range than the new incoming DF
        for filter_name, filter_obj in self.param.objects().items():
            if filter_name in self.df.columns:
                if isinstance(filter_obj, param.Range):
                    filtered_min_max = (
                        self.df_filtered[filter_name].min(),
                        self.df_filtered[filter_name].max(),
                    )
                    if init_value_range:
                        orig_min_max = (
                            self.df[filter_name].min(),
                            self.df[filter_name].max(),
                        )
                        filter_obj.bounds = filter_obj.softbounds = (None, None)
                        setattr(self, filter_name, filtered_min_max)
                        filter_obj.bounds = filter_obj.softbounds = orig_min_max
                    else:
                        setattr(self, filter_name, filtered_min_max)

                elif isinstance(filter_obj, param.ListSelector):
                    filtered_available_entries = np.unique(
                        self.df_filtered[filter_name]
                    ).tolist()
                    if init_value_range:
                        orig_available_entries = np.unique(
                            self.df[filter_name]
                        ).tolist()
                        setattr(self, filter_name, [])
                        filter_obj.objects = orig_available_entries
                    setattr(self, filter_name, filtered_available_entries)

                else:
                    print(f"TRAP: Unexpected filter_obj: {filter}")

        # re-enable watcher if UI is already up and running
        if self.ui is not None:
            self._watcher_filters = self.param.watch_values(
                self.apply_filter, parameter_names=list(self.df.columns)
            )

    def apply_filter(self, *args, **kwargs):
        """Reads and applies the filter.
        Triggered by changes to the parameter value, typically through the linked widget.
        """
        DEBUG(f"apply_filter(args={args}, kwargs={kwargs})")

        # The USER has changed a FILTER. In order to support the different use-cases:
        # a) simply filter once with one filter
        # b) filter down multiple times with same/different filters
        # c) back-out some filterting down
        # ....
        # we either need to remember and redo  filter changes the User did
        # or alternatively always just apply the user adjusted and automatically adjusted
        # filters (more DF filtering effort, but less coding)
        df_newly_filtered = self.df

        for column in self.df.columns:
            param_obj = getattr(self.param, column, None)

            if isinstance(param_obj, param.Range):
                start, end = getattr(self, column)
                df_newly_filtered = df_newly_filtered[
                    (df_newly_filtered[column] >= start)
                    & (df_newly_filtered[column] <= end)
                ]
            elif isinstance(param_obj, param.ListSelector):
                selected_values = getattr(self, column)
                df_newly_filtered = df_newly_filtered[
                    df_newly_filtered[column].isin(selected_values)
                ]

        self.df_filtered = df_newly_filtered
        print(f"df_filtered.shape={self.df_filtered.shape}")

        # adjust filter values to reflect the value-ranges on the filtered df-subset
        # may be optional
        self.adjust_filters()

    def view(self):
        """ """
        DEBUG("view()")
        if self.df is None:
            # nothing to do yet (no DF and hence no filters set)
            return

        # create the UI container the same throught lifecycle, just clear content if
        # redoing everything
        if self.ui is None:
            self.ui = pn.Row()
        else:
            self.ui.clear()

        self.ui.extend(
            [
                pn.Column(
                    pn.widgets.Button.from_param(self.param.reset_filters),
                    pn.Param(self.param, parameters=list(self.df.columns)),
                ),
                pn.widgets.Tabulator.from_param(
                    self.param.df_filtered,
                    header_filters=True,
                    disabled=True,
                    pagination="remote",
                ),
            ]
        )

        # activate Watcher to handle Filter Widget changes:
        self._watcher_filters = self.param.watch_values(
            self.apply_filter, parameter_names=list(self.df.columns)
        )

        return self.ui


hard = HardcodedDataframeFilter(df=df)
hard.view()
